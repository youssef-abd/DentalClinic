@echo off
echo ========================================
echo DentisteDB Installation Script
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r pyqt_dental_app\requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error installing dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Initializing database...
python pyqt_dental_app\db_init.py
if %errorlevel% neq 0 (
    echo ❌ Error initializing database
    pause
    exit /b 1
)

echo.
echo Step 3: Testing installation...
python -c "import pyqt_dental_app; print('✅ Installation successful!')"
if %errorlevel% neq 0 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo To run the application:
echo   python run_dental_app.py
echo.
echo Default login:
echo   Username: mouna
echo   Password: 123
echo.
pause
