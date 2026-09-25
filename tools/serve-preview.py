"""Serve the staged site locally with byte ranges for scroll-scrubbed films.

Run ``python tools/serve-preview.py --port 8878`` after stage-deploy.py.
The standard library's plain http.server ignores Range requests, leaving
HTMLVideoElement.seekable at zero in Chrome even after the whole film loads.
"""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self._range_length = None
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()

        try:
            file = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        try:
            stat = os.fstat(file.fileno())
            size = stat.st_size
            byte_range = self.headers.get("Range")
            selected = self._parse_range(byte_range, size) if byte_range else None
            if byte_range and selected is None:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                file.close()
                return None

            self.send_response(206 if selected else 200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
            if selected:
                start, end = selected
                self._range_length = end - start + 1
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(self._range_length))
                file.seek(start)
            else:
                self.send_header("Content-Length", str(size))
            self.end_headers()
            return file
        except Exception:
            file.close()
            raise

    @staticmethod
    def _parse_range(header, size):
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", header.strip())
        if not match or not size or not any(match.groups()):
            return None
        first, last = match.groups()
        if first:
            start = int(first)
            end = min(int(last), size - 1) if last else size - 1
        else:
            length = int(last)
            if length == 0:
                return None
            start, end = max(0, size - length), size - 1
        return (start, end) if start < size and start <= end else None

    def copyfile(self, source, outputfile):
        remaining = self._range_length
        if remaining is None:
            return super().copyfile(source, outputfile)
        while remaining:
            chunk = source.read(min(128 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8878)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1] / "_site")
    args = parser.parse_args()
    directory = args.directory.resolve()
    if not (directory / "captures.html").is_file():
        parser.error(f"no staged Captures page in {directory}; run tools/stage-deploy.py first")
    handler = partial(PreviewHandler, directory=str(directory))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"Preview: http://{args.host}:{args.port}/captures.html", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
