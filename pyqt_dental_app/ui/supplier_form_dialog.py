"""
Supplier Form Dialog
Dialog for adding/editing expense suppliers
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QTextEdit, QPushButton, QLabel,
                            QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SupplierFormDialog(QDialog):
    """Dialog for adding/editing expense suppliers"""
    
    def __init__(self, expense_service, supplier=None, parent=None):
        super().__init__(parent)
        self.expense_service = expense_service
        self.supplier = supplier
        self.is_edit_mode = supplier is not None
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.populate_form()
    
    def init_ui(self):
        """Initialize the user interface"""
        title = "Modifier le Fournisseur" if self.is_edit_mode else "Nouveau Fournisseur"
        self.setWindowTitle(title)
        self.setFixedSize(450, 400)
        
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
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du fournisseur...")
        form_layout.addRow("Nom:", self.name_edit)
        
        # Contact person
        self.contact_edit = QLineEdit()
        self.contact_edit.setPlaceholderText("Personne de contact...")
        form_layout.addRow("Contact:", self.contact_edit)
        
        # Phone
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Numéro de téléphone...")
        form_layout.addRow("Téléphone:", self.phone_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Adresse email...")
        form_layout.addRow("Email:", self.email_edit)
        
        # Address
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        self.address_edit.setPlaceholderText("Adresse complète...")
        form_layout.addRow("Adresse:", self.address_edit)
        
        # Tax ID
        self.tax_id_edit = QLineEdit()
        self.tax_id_edit.setPlaceholderText("Numéro fiscal...")
        form_layout.addRow("N° Fiscal:", self.tax_id_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
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
        save_btn.clicked.connect(self.save_supplier)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def populate_form(self):
        """Populate form with supplier data (edit mode)"""
        if not self.supplier:
            return
        
        self.name_edit.setText(self.supplier.name or "")
        self.contact_edit.setText(self.supplier.contact_person or "")
        self.phone_edit.setText(self.supplier.phone or "")
        self.email_edit.setText(self.supplier.email or "")
        self.address_edit.setPlainText(self.supplier.address or "")
        self.tax_id_edit.setText(self.supplier.tax_id or "")
        self.notes_edit.setPlainText(self.supplier.notes or "")
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom du fournisseur est obligatoire.")
            return False
        
        return True
    
    def save_supplier(self):
        """Save supplier"""
        if not self.validate_form():
            return
        
        try:
            name = self.name_edit.text().strip()
            contact_person = self.contact_edit.text().strip() or None
            phone = self.phone_edit.text().strip() or None
            email = self.email_edit.text().strip() or None
            address = self.address_edit.toPlainText().strip() or None
            tax_id = self.tax_id_edit.text().strip() or None
            notes = self.notes_edit.toPlainText().strip() or None
            
            if self.is_edit_mode:
                # Update existing supplier
                self.expense_service.update_supplier(
                    self.supplier.id,
                    name=name,
                    contact_person=contact_person,
                    phone=phone,
                    email=email,
                    address=address,
                    tax_id=tax_id,
                    notes=notes
                )
                QMessageBox.information(self, "Succès", "Fournisseur modifié avec succès!")
            else:
                # Create new supplier
                self.expense_service.create_supplier(
                    name=name,
                    contact_person=contact_person,
                    phone=phone,
                    email=email,
                    address=address,
                    tax_id=tax_id,
                    notes=notes
                )
                QMessageBox.information(self, "Succès", "Fournisseur ajouté avec succès!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
