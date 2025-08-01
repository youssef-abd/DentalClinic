@echo off
echo Installing Invoice Dependencies for DentisteDB...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Install python-docx for invoice generation
echo Installing python-docx...
pip install python-docx==0.8.11

if errorlevel 1 (
    echo ERROR: Failed to install python-docx
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo SUCCESS: Invoice dependencies installed successfully!
echo.
echo You can now use the invoice feature in DentisteDB:
echo 1. Open a patient's details
echo 2. Click the "Create Invoice" button
echo 3. Select visits and generate invoices
echo.
pause 