@echo off
for /f "tokens=*" %%i in ('dir/s/b/ad^|sort /r') do rd "%%i"