REM cd /d C:\Users\YEN\Desktop\Crawler\Pchome
REM call activate dev

cd /d %~dp0
cd ../
REM call bin\venv\Scripts\activate dev
call python screen.py
call python ssd.py
call python ram.py