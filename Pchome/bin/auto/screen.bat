REM cd /d C:\Users\YEN\Desktop\Crawler\Pchome
REM call activate dev

cd /d %~dp0
cd ../..
bin\venv\Scripts\activate
call python screen.py
pause
