# DentisteDB - Installation Guide

## 📦 Installation Options

### Option 1: Standalone Executable (Recommended for End Users)
### Option 2: Python Source Installation (For Developers)
### Option 3: Portable Installation

---

## 🚀 Option 1: Standalone Executable (Easiest)

### Step 1: Create Executable (On Development PC)

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Create the executable:**
   ```bash
   pyinstaller --onefile --windowed --name="DentisteDB" run_dental_app.py
   ```

3. **Advanced packaging with icon and resources:**
   ```bash
   pyinstaller --onefile --windowed --name="DentisteDB" --icon=icon.ico --add-data="pyqt_dental_app;pyqt_dental_app" run_dental_app.py
   ```

### Step 2: Deploy to Target PC

1. **Copy files to target PC:**
   ```
   DentisteDB_Portable/
   ├── DentisteDB.exe           # Main executable
   ├── db_init.py              # Database initialization
   ├── update_database.py      # Database migration
   └── README_USER.txt         # User instructions
   ```

2. **First run on target PC:**
   ```bash
   # Initialize database
   python db_init.py
   
   # Run application
   DentisteDB.exe
   ```

---

## 🐍 Option 2: Python Source Installation

### Prerequisites on Target PC:
- Python 3.8+ installed
- pip package manager

### Step 1: Copy Project Files
Copy the entire project folder to the target PC:
```
DentisteDB/
├── pyqt_dental_app/         # Main application package
├── run_dental_app.py        # Application launcher
├── db_init.py              # Database initialization
├── update_database.py      # Database migration
├── requirements.txt        # Dependencies (create this)
└── README.md               # Documentation
```

### Step 2: Install Dependencies
```bash
# Navigate to project directory
cd DentisteDB

# Install required packages
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
python db_init.py
```

### Step 4: Run Application
```bash
python run_dental_app.py
```

---

## 📱 Option 3: Portable Installation

### Create Portable Package (On Development PC)

1. **Create virtual environment:**
   ```bash
   python -m venv dental_portable
   dental_portable\Scripts\activate
   pip install PyQt5 SQLAlchemy Werkzeug
   ```

2. **Copy application files:**
   ```
   DentisteDB_Portable/
   ├── python_portable/        # Portable Python + dependencies
   ├── pyqt_dental_app/       # Application code
   ├── run_dental_app.py      # Launcher
   ├── start_app.bat          # Windows batch file
   └── README.txt             # Instructions
   ```

3. **Create start_app.bat:**
   ```batch
   @echo off
   cd /d "%~dp0"
   python_portable\Scripts\python.exe run_dental_app.py
   pause
   ```

---

## 📋 Requirements File

Create `requirements.txt`:
```txt
PyQt5==5.15.9
SQLAlchemy==2.0.23
Werkzeug==3.0.1
```

---

## 🔧 Installation Scripts

### Windows Installer Script (install.bat)
```batch
@echo off
echo Installing DentisteDB - Dental Cabinet Management System
echo =====================================================

echo.
echo Step 1: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Initializing database...
python db_init.py

echo.
echo Step 3: Testing installation...
python -c "import pyqt_dental_app; print('✅ Installation successful!')"

echo.
echo Installation completed!
echo Run the application with: python run_dental_app.py
pause
```

### Linux/Mac Installer Script (install.sh)
```bash
#!/bin/bash
echo "Installing DentisteDB - Dental Cabinet Management System"
echo "====================================================="

echo ""
echo "Step 1: Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Step 2: Initializing database..."
python3 db_init.py

echo ""
echo "Step 3: Testing installation..."
python3 -c "import pyqt_dental_app; print('✅ Installation successful!')"

echo ""
echo "Installation completed!"
echo "Run the application with: python3 run_dental_app.py"
```

---

## 🗂️ Data Migration

### Transferring Existing Data

If you have existing patient data:

1. **Copy database file:**
   ```bash
   # From: ~/.dentistedb/patients.db
   # To: target_pc/.dentistedb/patients.db
   ```

2. **Copy X-ray images:**
   ```bash
   # From: ~/.dentistedb/xrays/
   # To: target_pc/.dentistedb/xrays/
   ```

3. **Run database migration:**
   ```bash
   python update_database.py
   ```

---

## 🔒 Security Considerations

### For Production Deployment:

1. **Change default admin password:**
   - Default: username=`mouna`, password=`123`
   - Change on first login

2. **Set proper file permissions:**
   ```bash
   # Protect database and X-ray files
   chmod 600 ~/.dentistedb/patients.db
   chmod 700 ~/.dentistedb/xrays/
   ```

3. **Regular backups:**
   - Database: `~/.dentistedb/patients.db`
   - X-rays: `~/.dentistedb/xrays/`

---

## 🆘 Troubleshooting

### Common Issues:

1. **"PyQt5 not found":**
   ```bash
   pip install PyQt5
   ```

2. **"Database not found":**
   ```bash
   python db_init.py
   ```

3. **"Permission denied":**
   - Run as administrator (Windows)
   - Use `sudo` (Linux/Mac)

4. **"Application won't start":**
   ```bash
   # Check Python version
   python --version  # Should be 3.8+
   
   # Test imports
   python -c "import PyQt5; print('PyQt5 OK')"
   ```

---

## 📞 Support

For installation issues:
1. Check Python version (3.8+ required)
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Check system compatibility (Windows 10+, macOS 10.14+, Ubuntu 18.04+)

---

## 🎯 Quick Start Commands

### For End Users (Executable):
```bash
1. Double-click DentisteDB.exe
2. Login with: mouna / 123
3. Change password on first login
```

### For Developers (Source):
```bash
1. pip install -r requirements.txt
2. python db_init.py
3. python run_dental_app.py
```
