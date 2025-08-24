@echo off
echo ========================================
echo DentisteDB Executable Creator
echo ========================================
echo.

echo Installing PyInstaller...
python -m pip install --upgrade pip
pip install pyinstaller==5.13.2
if %errorlevel% neq 0 (
    echo ❌ Error installing PyInstaller
    pause
    exit /b 1
)

echo.
echo Creating standalone executable...
pyinstaller --onefile --windowed --name="DentisteDB" --hidden-import PyQt5.sip --hidden-import PyQt5.QtPrintSupport --add-data="pyqt_dental_app;pyqt_dental_app" run_dental_app.py
if %errorlevel% neq 0 (
    echo ❌ Error creating executable
    pause
    exit /b 1
)

echo.
echo ✅ Executable created successfully!
echo.
echo Location: dist\DentisteDB.exe
echo.
echo To deploy to another PC:
echo 1. Copy dist\DentisteDB.exe to the target PC
echo 2. Double-click DentisteDB.exe to run the app
echo.
pause
