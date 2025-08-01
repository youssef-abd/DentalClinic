"""
Change Password Dialog

A dialog for users to change their password
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class ChangePasswordDialog(QDialog):
    """Dialog for changing the user's password"""
    
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("Changer le mot de passe")
        self.setMinimumWidth(400)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Form layout for input fields
        form_layout = QFormLayout()
        
        # Current password
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Mot de passe actuel:", self.current_password_edit)
        
        # New password
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Nouveau mot de passe:", self.new_password_edit)
        
        # Confirm new password
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirmer le nouveau mot de passe:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.change_password)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def change_password(self):
        """Handle password change"""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validate inputs
        if not current_password:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer votre mot de passe actuel")
            return
            
        if not new_password:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nouveau mot de passe")
            return
            
        if new_password != confirm_password:
            QMessageBox.warning(self, "Erreur", "Les nouveaux mots de passe ne correspondent pas")
            return
            
        # Attempt to change password
        success, message = self.auth_service.change_password(current_password, new_password)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)
