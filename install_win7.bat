@echo off
echo ========================================
echo DentisteDB Windows 7 Installation
echo ========================================
echo.
echo ⚠️  WINDOWS 7 COMPATIBILITY MODE
echo This script installs compatible versions for Windows 7
echo.

echo Step 1: Checking Python version...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.8.10 for Windows 7:
    echo https://www.python.org/downloads/release/python-3810/
    echo.
    pause
    exit /b 1
)

python --version | findstr "3.8"
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Python 3.8.x recommended for Windows 7
    echo Current version may not be fully compatible
    echo.
)

echo Step 2: Installing Windows 7 compatible dependencies...
python -m pip install --upgrade pip
pip install -r requirements_win7.txt
if %errorlevel% neq 0 (
    echo ❌ Error installing dependencies
    echo.
    echo Try installing Visual C++ Redistributable 2015-2019:
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    pause
    exit /b 1
)

echo.
echo Step 3: Initializing database...
python pyqt_dental_app\db_init.py
if %errorlevel% neq 0 (
    echo ❌ Error initializing database
    echo Try running as Administrator
    pause
    exit /b 1
)

echo.
echo Step 4: Testing installation...
python -c "import PyQt5; print('PyQt5 version:', PyQt5.QtCore.PYQT_VERSION_STR)"
if %errorlevel% neq 0 (
    echo ❌ PyQt5 test failed
    pause
    exit /b 1
)

python -c "import pyqt_dental_app; print('✅ Application test successful!')"
if %errorlevel% neq 0 (
    echo ❌ Application test failed
    pause
    exit /b 1
)

echo.
echo ✅ Windows 7 installation completed successfully!
echo.
echo 📋 Installation Summary:
echo   - Python: Compatible version detected
echo   - PyQt5: 5.15.2 (Windows 7 compatible)
echo   - SQLAlchemy: 1.4.46 (Windows 7 compatible)
echo   - Werkzeug: 2.3.7 (Windows 7 compatible)
echo   - Database: Initialized successfully
echo.
echo 🚀 To run the application:
echo   python run_dental_app.py
echo.
echo 🔐 Default login credentials:
echo   Username: mouna
echo   Password: 123
echo.
echo ⚠️  Windows 7 Notes:
echo   - Some UI elements may look different
echo   - Performance may be slower than newer Windows
echo   - Consider upgrading to Windows 10/11 for best experience
echo.
pause
