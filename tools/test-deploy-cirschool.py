#!/usr/bin/env python3
"""Tests for how tools/deploy-cirschool.py behaves when the host drops the connection.

cirschool.org's host closes an FTPS session after roughly sixty uploads. The
next command meets a closed socket and ftplib raises EOFError. A publish of a
few hundred files met that several times and, before this was handled, died at
the first one. These tests stand in for the host: a fake FTP connection that
hangs up after a set number of uploads, so the reconnect can be checked without
touching the real site.

    python3 tools/test-deploy-cirschool.py
"""

import ftplib
import importlib.util
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("deploy_cirschool", os.path.join(HERE, "deploy-cirschool.py"))
tool = importlib.util.module_from_spec(spec)
sys.modules["deploy_cirschool"] = tool
spec.loader.exec_module(tool)

SETTINGS = {"CIRS_FTP_HOST": "ftp.example.test", "CIRS_FTP_PORT": "21", "CIRS_FTP_ROOT": "/",
            "CIRS_FTP_USER": "u", "CIRS_FTP_TLS_HOSTNAME": "ftp.example.test"}


class Server:
    """What the host holds, and how many sessions it has handed out."""

    def __init__(self, uploads_per_session=None):
        self.files = {}
        self.dirs = set()
        self.sessions = 0
        self.uploads_per_session = uploads_per_session


class FakeFTP:
    """One session. After `uploads_per_session` stores the host hangs up, and
    the next command raises EOFError, as ftplib does on a closed connection."""

    def __init__(self, server):
        self.server = server
        server.sessions += 1
        self.stored = 0
        self.sock = object()
        self.closed = False

    def _alive(self):
        if self.sock is None:
            raise AttributeError("'NoneType' object has no attribute 'sendall'")
        limit = self.server.uploads_per_session
        if limit is not None and self.stored >= limit:
            raise EOFError()

    def mkd(self, path):
        self._alive()
        self.server.dirs.add(path)

    def storbinary(self, cmd, fp, blocksize=8192):
        self._alive()
        path = cmd[len("STOR "):]
        self.server.files[path] = fp.read()
        self.stored += 1

    def quit(self):
        self._alive()
        self.close()

    def close(self):
        self.sock = None
        self.closed = True


def make_uploader(server, **kw):
    first = FakeFTP(server)
    reconnect = kw.pop("reconnect", lambda: FakeFTP(server))
    return tool.Uploader(first, SETTINGS, reconnect=reconnect, **kw)


class UploaderReconnects(unittest.TestCase):
    def setUp(self):
        self._sleep = tool.time.sleep
        tool.time.sleep = lambda s: None          # no waiting in a test
        self._say = tool.say
        self.log = []
        tool.say = self.log.append

    def tearDown(self):
        tool.time.sleep = self._sleep
        tool.say = self._say

    def test_every_file_arrives_once_whole_when_the_host_keeps_hanging_up(self):
        server = Server(uploads_per_session=3)
        up = make_uploader(server)
        sent = {f"assets/img/arts/photo-{i:03d}.webp": bytes([i]) * (50 + i) for i in range(40)}
        for rel, data in sent.items():
            up.put(rel, data)
        self.assertEqual(len(server.files), 40)
        for rel, data in sent.items():
            self.assertEqual(server.files["/" + rel], data, rel)
        # 40 files, 3 per session: the first session plus 13 more.
        self.assertEqual(up.reconnects, 13)
        self.assertEqual(server.sessions, 14)
        self.assertEqual(sum("logging in again" in line for line in self.log), 13)

    def test_directories_are_not_made_again_after_a_reconnect(self):
        server = Server(uploads_per_session=1)
        up = make_uploader(server)
        for i in range(4):
            up.put(f"assets/img/arts/p{i}.webp", b"x")
        self.assertEqual(server.dirs, {"/assets", "/assets/img", "/assets/img/arts"})

    def test_a_host_that_never_recovers_stops_the_run_with_a_plain_message(self):
        server = Server(uploads_per_session=0)         # every session is dead on arrival
        up = make_uploader(server)
        with self.assertRaises(SystemExit) as stopped:
            up.put("index.html", b"<html>")
        message = str(stopped.exception)
        self.assertIn("could not send index.html", message)
        self.assertIn("running the same command again is safe", message)
        self.assertEqual(up.reconnects, tool.SEND_ATTEMPTS - 1)

    def test_a_refusal_is_not_retried(self):
        server = Server()
        up = make_uploader(server)

        def refuse(cmd, fp, blocksize=8192):
            raise ftplib.error_perm("552 Disk quota exceeded")
        up.ftp.storbinary = refuse
        with self.assertRaises(SystemExit) as stopped:
            up.put("index.html", b"<html>")
        self.assertIn("refused index.html", str(stopped.exception))
        self.assertEqual(up.reconnects, 0)

    def test_without_a_way_to_reconnect_a_drop_still_stops_cleanly(self):
        server = Server(uploads_per_session=0)
        up = tool.Uploader(FakeFTP(server), SETTINGS)
        with self.assertRaises(SystemExit):
            up.put("index.html", b"<html>")

    def test_close_copes_with_a_connection_the_host_already_dropped(self):
        server = Server(uploads_per_session=1)
        up = make_uploader(server)
        up.put("a.txt", b"1")
        up.ftp.close()                                  # the host or a reconnect closed it
        up.close()                                      # must not raise
        up2 = make_uploader(Server(uploads_per_session=1))
        up2.put("a.txt", b"1")                          # now at its limit: quit() meets EOFError
        up2.close()                                     # must not raise either


class LoginAfterADrop(unittest.TestCase):
    def setUp(self):
        self._sleep = tool.time.sleep
        tool.time.sleep = lambda s: None
        self._FTPS = tool.FTPS
        self.attempts = 0

    def tearDown(self):
        tool.time.sleep = self._sleep
        tool.FTPS = self._FTPS

    def fake_ftps(self, fail_first, error):
        outer = self

        class Fake:
            def __init__(self, context=None, timeout=None):
                outer.attempts += 1
                self.n = outer.attempts
                self.closed = False

            def connect(self, host, port):
                if self.n <= fail_first:
                    raise error

            def login(self, user, password):
                pass

            def prot_p(self):
                pass

            def set_pasv(self, on):
                pass

            def close(self):
                self.closed = True
        return Fake

    def test_a_patient_login_tries_again_when_the_old_session_is_still_closing(self):
        tool.FTPS = self.fake_ftps(2, ftplib.error_temp("421 Too many connections"))
        ftp = tool.connect(SETTINGS, "pw", patient=True)
        self.assertEqual(self.attempts, 3)
        self.assertFalse(ftp.closed)

    def test_the_first_login_is_not_patient(self):
        tool.FTPS = self.fake_ftps(1, ConnectionResetError())
        with self.assertRaises(SystemExit):
            tool.connect(SETTINGS, "pw")
        self.assertEqual(self.attempts, 1)

    def test_a_refused_password_is_never_retried(self):
        class Refusing(self.fake_ftps(0, None)):
            def login(self, user, password):
                raise ftplib.error_perm("530 Login incorrect")
        tool.FTPS = Refusing
        with self.assertRaises(SystemExit) as stopped:
            tool.connect(SETTINGS, "pw", patient=True)
        self.assertIn("refused the login", str(stopped.exception))
        self.assertEqual(self.attempts, 1)

    def test_a_patient_login_gives_up_after_its_attempts(self):
        tool.FTPS = self.fake_ftps(99, EOFError())
        with self.assertRaises(SystemExit):
            tool.connect(SETTINGS, "pw", patient=True)
        self.assertEqual(self.attempts, tool.LOGIN_ATTEMPTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
