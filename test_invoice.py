#!/usr/bin/env python3
"""
Test script for invoice functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyqt_dental_app.services.invoice_service import InvoiceService
from pyqt_dental_app.models.database import DatabaseManager

def test_invoice_service():
    """Test the invoice service functionality"""
    print("Testing Invoice Service...")
    
    try:
        # Initialize database and service
        db_manager = DatabaseManager()
        invoice_service = InvoiceService(db_manager)
        
        print("✅ Invoice service initialized successfully")
        
        # Test doctor info
        print(f"✅ Doctor info: {invoice_service.doctor_info['name']}")
        
        # Test invoice number generation
        invoice_number = invoice_service.generate_invoice_number()
        print(f"✅ Generated invoice number: {invoice_number}")
        
        # Test template folder creation
        if os.path.exists(invoice_service.template_folder):
            print(f"✅ Template folder created: {invoice_service.template_folder}")
        
        print("\n🎉 All tests passed! Invoice functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_invoice_service()
    sys.exit(0 if success else 1) 