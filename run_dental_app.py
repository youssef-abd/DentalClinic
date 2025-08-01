#!/usr/bin/env python3
"""
Entry point script for PyQt Dental Cabinet Application
Run this script to start the dental practice management application
"""

import sys
import os

# Add the application directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Import and run the main application
from pyqt_dental_app.main import main

if __name__ == "__main__":
    print("🏥 Démarrage de DentisteDB - Gestion de Cabinet Dentaire")
    print("=" * 60)
    main()
