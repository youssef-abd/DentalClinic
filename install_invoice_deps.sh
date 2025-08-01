#!/bin/bash

echo "Installing Invoice Dependencies for DentisteDB..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "Python found. Installing dependencies..."
echo

# Install python-docx for invoice generation
echo "Installing python-docx..."
pip3 install python-docx==0.8.11

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install python-docx"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "SUCCESS: Invoice dependencies installed successfully!"
echo
echo "You can now use the invoice feature in DentisteDB:"
echo "1. Open a patient's details"
echo "2. Click the 'Create Invoice' button"
echo "3. Select visits and generate invoices"
echo 