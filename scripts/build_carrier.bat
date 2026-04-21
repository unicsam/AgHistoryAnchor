@echo off
echo ====================================================
echo  BUILDING AG HISTORY CARRIER STUB
echo ====================================================

:: Use PyInstaller to build the carrier script into a standalone EXE
:: We use --onefile and --noconsole for a clean stub
python -m PyInstaller --onefile --noconsole ^
    --name carrier_stub ^
    "%~dp0\..\ag_history\operations\carrier.py"

echo.
echo [OK] Building complete. 
move /Y dist\carrier_stub.exe "%~dp0\.."
echo [OK] Carrier landed in root: carrier_stub.exe
pause
