@echo off
setlocal

cd /d "%~dp0"
set "WRANGLER_LOG_PATH=.wrangler\wrangler.log"

echo Starting Orch Terminology website...
npx vinext dev

if errorlevel 1 pause
endlocal
