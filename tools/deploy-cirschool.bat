@echo off
rem Double-click to publish the latest main to cirschool.org.
rem It lists what will change and asks before uploading anything.
rem First time on a computer? Run "deploy-cirschool.bat --setup --from-filezilla" once,
rem then "deploy-cirschool.bat --baseline" once (only the very first time ever).
cd /d "%~dp0\.."
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% -m pip install --quiet --disable-pip-version-check brotli keyring
%PY% tools\deploy-cirschool.py %*
echo.
pause
