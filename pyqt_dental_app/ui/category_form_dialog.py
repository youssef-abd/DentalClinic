"""
Category Form Dialog
Dialog for adding/editing expense categories
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QTextEdit, QPushButton, QLabel,
                            QMessageBox, QFrame, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class CategoryFormDialog(QDialog):
    """Dialog for adding/editing expense categories"""
    
    def __init__(self, expense_service, category=None, parent=None):
        super().__init__(parent)
        self.expense_service = expense_service
        self.category = category
        self.is_edit_mode = category is not None
        self.selected_color = "#3B82F6"  # Default blue
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.populate_form()
    
    def init_ui(self):
        """Initialize the user interface"""
        title = "Modifier la Catégorie" if self.is_edit_mode else "Nouvelle Catégorie"
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        
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
        self.name_edit.setPlaceholderText("Nom de la catégorie...")
        form_layout.addRow("Nom:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description de la catégorie...")
        form_layout.addRow("Description:", self.description_edit)
        
        # Color
        color_layout = QHBoxLayout()
        self.color_preview = QLabel("   ")
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc; border-radius: 3px;")
        self.color_preview.setFixedSize(30, 25)
        
        color_btn = QPushButton("Choisir Couleur")
        color_btn.clicked.connect(self.select_color)
        
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(color_btn)
        color_layout.addStretch()
        
        form_layout.addRow("Couleur:", color_layout)
        
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
        save_btn.clicked.connect(self.save_category)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def populate_form(self):
        """Populate form with category data (edit mode)"""
        if not self.category:
            return
        
        self.name_edit.setText(self.category.name or "")
        self.description_edit.setPlainText(self.category.description or "")
        
        if self.category.color:
            self.selected_color = self.category.color
            self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc; border-radius: 3px;")
    
    def select_color(self):
        """Select color for category"""
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc; border-radius: 3px;")
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom de la catégorie est obligatoire.")
            return False
        
        return True
    
    def save_category(self):
        """Save category"""
        if not self.validate_form():
            return
        
        try:
            name = self.name_edit.text().strip()
            description = self.description_edit.toPlainText().strip() or None
            color = self.selected_color
            
            if self.is_edit_mode:
                # Update existing category
                self.expense_service.update_category(
                    self.category.id,
                    name=name,
                    description=description,
                    color=color
                )
                QMessageBox.information(self, "Succès", "Catégorie modifiée avec succès!")
            else:
                # Create new category
                self.expense_service.create_category(
                    name=name,
                    description=description,
                    color=color
                )
                QMessageBox.information(self, "Succès", "Catégorie ajoutée avec succès!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
