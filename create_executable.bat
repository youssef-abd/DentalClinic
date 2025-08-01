@echo off
echo ========================================
echo DentisteDB Executable Creator
echo ========================================
echo.

echo Installing PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ Error installing PyInstaller
    pause
    exit /b 1
)

echo.
echo Creating standalone executable...
pyinstaller --onefile --windowed --name="DentisteDB" --add-data="pyqt_dental_app;pyqt_dental_app" run_dental_app.py
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
echo 1. Copy dist\DentisteDB.exe to target PC
echo 2. Copy pyqt_dental_app\db_init.py to target PC
echo 3. Run db_init.py on target PC first
echo 4. Then run DentisteDB.exe
echo.
pause
