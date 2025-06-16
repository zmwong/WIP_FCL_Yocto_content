@echo off
set "EFI_Mode=CR"


echo Attempting to change the boot order ...
timeout /t 5 /nobreak
C:\validation\station-automation\automation\biosrunner\target_runner.py --program --ini=knobs_mmex_cr.ini --save-xml

echo Enabling memtest switch for CR
timeout /t 5 /nobreak
C:\validation\windows-test-content\memory\mtl_s\memtest.py --command %EFI_Mode% --loop 0

if %errorlevel% neq 0 (
	echo Error occured during Boot order change / EFI switches
	timeout /t 15 /nobreak
)

echo Starting mmex.py script from mtl_s validation directory ...
timeout /t 5 /nobreak
start cmd.exe /k "C:\validation\windows-test-content\memory\mtl_s\mmex.py"



set /a duration_seconds = 11300
:loop
cls
echo Rebooting to EFI in %duration_seconds% seconds
timeout /t 1 /nobreak >nul
set /a duration_seconds -=1
if %duration_seconds% gtr 0 goto loop
shutdown /r /f /t 0