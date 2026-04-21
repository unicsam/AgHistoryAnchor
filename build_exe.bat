@echo off
echo ====================================================
echo  AG HISTORY ANCHOR: EXE BUILDER
echo ====================================================

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
)

echo [i] Building Standalone EXE...
python -m PyInstaller --onefile --name AgHistoryAnchor --icon ag_anchor.ico --clean AgHistoryAnchor.py

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build Complete!
    echo [i] Executable is in the 'dist' folder.
) else (
    echo.
    echo [!] Build FAILED.
)

pause
