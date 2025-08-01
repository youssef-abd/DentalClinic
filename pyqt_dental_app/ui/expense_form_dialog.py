"""
Expense Form Dialog
Dialog for adding/editing expenses
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QTextEdit, QComboBox, QDateEdit,
                            QDoubleSpinBox, QCheckBox, QPushButton, QLabel,
                            QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime
import os

class ExpenseFormDialog(QDialog):
    """Dialog for adding/editing expenses"""
    
    def __init__(self, expense_service, expense=None, parent=None):
        super().__init__(parent)
        self.expense_service = expense_service
        self.expense = expense
        self.is_edit_mode = expense is not None
        self.receipt_file_path = None
        
        self.init_ui()
        self.load_data()
        
        if self.is_edit_mode:
            self.populate_form()
    
    def init_ui(self):
        """Initialize the user interface"""
        title = "Modifier la Dépense" if self.is_edit_mode else "Nouvelle Dépense"
        self.setWindowTitle(title)
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(title)
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Form
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Date:", self.date_edit)
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Description de la dépense...")
        form_layout.addRow("Description:", self.description_edit)
        
        # Amount
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0.01, 999999.99)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setSuffix(" MAD")
        form_layout.addRow("Montant:", self.amount_spinbox)
        
        # Category
        self.category_combo = QComboBox()
        form_layout.addRow("Catégorie:", self.category_combo)
        
        # Supplier
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Aucun fournisseur", None)
        form_layout.addRow("Fournisseur:", self.supplier_combo)
        
        # Invoice number
        self.invoice_edit = QLineEdit()
        self.invoice_edit.setPlaceholderText("Numéro de facture (optionnel)")
        form_layout.addRow("N° Facture:", self.invoice_edit)
        
        # Payment method
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["cash", "check", "card", "transfer"])
        form_layout.addRow("Mode de Paiement:", self.payment_combo)
        
        # Tax deductible
        self.tax_deductible_checkbox = QCheckBox("Déductible fiscalement")
        self.tax_deductible_checkbox.setChecked(True)
        form_layout.addRow("", self.tax_deductible_checkbox)
        
        # Tax amount
        self.tax_amount_spinbox = QDoubleSpinBox()
        self.tax_amount_spinbox.setRange(0.00, 999999.99)
        self.tax_amount_spinbox.setDecimals(2)
        self.tax_amount_spinbox.setSuffix(" MAD")
        form_layout.addRow("Montant TVA:", self.tax_amount_spinbox)
        
        # Receipt file
        receipt_layout = QHBoxLayout()
        self.receipt_label = QLabel("Aucun fichier sélectionné")
        self.receipt_label.setStyleSheet("color: #6B7280;")
        receipt_btn = QPushButton("📎 Joindre Reçu")
        receipt_btn.clicked.connect(self.select_receipt_file)
        receipt_layout.addWidget(self.receipt_label)
        receipt_layout.addWidget(receipt_btn)
        form_layout.addRow("Reçu:", receipt_layout)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Notes additionnelles...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addWidget(form_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Enregistrer" if self.is_edit_mode else "Ajouter")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        save_btn.clicked.connect(self.save_expense)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_data(self):
        """Load categories and suppliers"""
        try:
            # Load categories
            categories = self.expense_service.get_all_categories()
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
            
            # Load suppliers
            suppliers = self.expense_service.get_all_suppliers()
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.name, supplier.id)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def populate_form(self):
        """Populate form with expense data (edit mode)"""
        if not self.expense:
            return
        
        # Date
        if self.expense.date:
            self.date_edit.setDate(QDate.fromString(self.expense.date.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        
        # Description
        self.description_edit.setText(self.expense.description or "")
        
        # Amount
        self.amount_spinbox.setValue(self.expense.amount or 0.0)
        
        # Category
        if self.expense.category_id:
            index = self.category_combo.findData(self.expense.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        # Supplier
        if self.expense.supplier_id:
            index = self.supplier_combo.findData(self.expense.supplier_id)
            if index >= 0:
                self.supplier_combo.setCurrentIndex(index)
        
        # Invoice number
        self.invoice_edit.setText(self.expense.invoice_number or "")
        
        # Payment method
        if self.expense.payment_method:
            index = self.payment_combo.findText(self.expense.payment_method)
            if index >= 0:
                self.payment_combo.setCurrentIndex(index)
        
        # Tax deductible
        self.tax_deductible_checkbox.setChecked(self.expense.is_tax_deductible)
        
        # Tax amount
        self.tax_amount_spinbox.setValue(self.expense.tax_amount or 0.0)
        
        # Receipt file
        if self.expense.receipt_file and os.path.exists(self.expense.receipt_file):
            filename = os.path.basename(self.expense.receipt_file)
            self.receipt_label.setText(f"Fichier actuel: {filename}")
            self.receipt_file_path = self.expense.receipt_file
        
        # Notes
        self.notes_edit.setPlainText(self.expense.notes or "")
    
    def select_receipt_file(self):
        """Select receipt file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un reçu",
            "", "Images (*.png *.jpg *.jpeg);;PDF (*.pdf);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.receipt_file_path = file_path
            filename = os.path.basename(file_path)
            self.receipt_label.setText(f"Fichier sélectionné: {filename}")
    
    def validate_form(self):
        """Validate form data"""
        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Validation", "La description est obligatoire.")
            return False
        
        if self.amount_spinbox.value() <= 0:
            QMessageBox.warning(self, "Validation", "Le montant doit être supérieur à 0.")
            return False
        
        if self.category_combo.currentData() is None:
            QMessageBox.warning(self, "Validation", "Veuillez sélectionner une catégorie.")
            return False
        
        return True
    
    def save_expense(self):
        """Save expense"""
        if not self.validate_form():
            return
        
        try:
            # Prepare data
            date = self.date_edit.date().toPyDate()
            description = self.description_edit.text().strip()
            amount = self.amount_spinbox.value()
            category_id = self.category_combo.currentData()
            supplier_id = self.supplier_combo.currentData()
            invoice_number = self.invoice_edit.text().strip() or None
            payment_method = self.payment_combo.currentText()
            is_tax_deductible = self.tax_deductible_checkbox.isChecked()
            tax_amount = self.tax_amount_spinbox.value()
            notes = self.notes_edit.toPlainText().strip() or None
            
            if self.is_edit_mode:
                # Update existing expense
                self.expense_service.update_expense(
                    self.expense.id,
                    date=date,
                    description=description,
                    amount=amount,
                    category_id=category_id,
                    supplier_id=supplier_id,
                    invoice_number=invoice_number,
                    payment_method=payment_method,
                    is_tax_deductible=is_tax_deductible,
                    tax_amount=tax_amount,
                    notes=notes
                )
                
                # Handle receipt file
                if self.receipt_file_path and self.receipt_file_path != self.expense.receipt_file:
                    self.expense_service.save_receipt_file(self.expense.id, self.receipt_file_path)
                
                QMessageBox.information(self, "Succès", "Dépense modifiée avec succès!")
            else:
                # Create new expense
                expense_id = self.expense_service.create_expense(
                    date=date,
                    description=description,
                    amount=amount,
                    category_id=category_id,
                    supplier_id=supplier_id,
                    invoice_number=invoice_number,
                    payment_method=payment_method,
                    is_tax_deductible=is_tax_deductible,
                    tax_amount=tax_amount,
                    notes=notes
                )
                
                # Handle receipt file
                if self.receipt_file_path:
                    self.expense_service.save_receipt_file(expense_id, self.receipt_file_path)
                
                QMessageBox.information(self, "Succès", "Dépense ajoutée avec succès!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
