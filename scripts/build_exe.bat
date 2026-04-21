@echo off
echo ====================================================
echo  AG HISTORY ANCHOR: EXE BUILDER
echo ====================================================

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
)

echo [i] Checking dependencies...
if not exist "%~dp0\carrier_stub.exe" (
    if not exist "%~dp0\..\carrier_stub.exe" (
        echo [!] carrier_stub.exe missing. Building dependency first...
        call "%~dp0\build_carrier.bat"
    )
)

echo [i] Building Standalone EXE (Production Grade)...
python -m PyInstaller --onefile ^
    --name AgHistoryAnchor ^
    --icon "%~dp0\..\assets\ag_anchor.ico" ^
    --add-data "%~dp0\..\carrier_stub.exe;." ^
    --add-data "%~dp0\..\AgHistoryAnchor.py;." ^
    --add-data "%~dp0\..\ag_history;ag_history" ^
    --add-data "%~dp0\..\assets\ag_anchor.ico;." ^
    --clean ^
    "%~dp0\..\AgHistoryAnchor.py"

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build Complete!
    echo [i] Executable is in the 'dist' folder.
) else (
    echo.
    echo [!] Build FAILED.
)

pause
