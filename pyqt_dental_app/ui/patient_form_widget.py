"""
Patient form widget for adding and editing patients
Replaces add_patient.html and edit_patient.html templates with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox,
                            QFrame, QGroupBox, QScrollArea, QFileDialog, QSizePolicy, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap
import os

class PatientFormWidget(QWidget):
    """Widget for adding and editing patient information"""
    
    # Signals
    patient_saved = pyqtSignal(int)  # Emits patient ID
    form_cancelled = pyqtSignal()
    
    def __init__(self, patient_service):
        super().__init__()
        self.patient_service = patient_service
        self.current_patient_id = None
        self.is_edit_mode = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # Main widget inside scroll area
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        self.title_label = QLabel("Nouveau Patient")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")
        header_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Remplissez les informations du patient")
        self.subtitle_label.setStyleSheet("color: #666; font-size: 14px;")
        header_layout.addWidget(self.subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # Form section
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        
        # Personal Information Group
        personal_group = QGroupBox("Informations Personnelles")
        personal_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2E7D32;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        personal_layout = QFormLayout(personal_group)
        personal_layout.setSpacing(15)
        
        # Input field style
        input_style = """
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #4CAF50;
            }
        """
        
        # Personal information fields
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de famille")
        self.nom_input.setStyleSheet(input_style)
        personal_layout.addRow("Nom *:", self.nom_input)
        
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom")
        self.prenom_input.setStyleSheet(input_style)
        personal_layout.addRow("Prénom *:", self.prenom_input)
        
        date_naissance_label = QLabel("Date de Naissance:")
        self.date_naissance_input = QDateEdit()
        self.date_naissance_input.setCalendarPopup(True)
        self.date_naissance_input.setDate(QDate.currentDate().addYears(-30))  # Default to 30 years ago
        personal_layout.addRow(date_naissance_label, self.date_naissance_input)
        
        self.telephone_input = QLineEdit()
        self.telephone_input.setPlaceholderText("Numéro de téléphone")
        self.telephone_input.setStyleSheet(input_style)
        personal_layout.addRow("Téléphone:", self.telephone_input)
        
        self.carte_input = QLineEdit()
        self.carte_input.setPlaceholderText("Numéro de carte nationale")
        self.carte_input.setStyleSheet(input_style)
        personal_layout.addRow("Carte Nationale:", self.carte_input)
        
        form_layout.addWidget(personal_group)
        
        # Professional Information Group
        professional_group = QGroupBox("Informations Professionnelles")
        professional_group.setStyleSheet(personal_group.styleSheet())
        professional_layout = QFormLayout(professional_group)
        professional_layout.setSpacing(15)
        
        self.assurance_input = QLineEdit()
        self.assurance_input.setPlaceholderText("Compagnie d'assurance")
        self.assurance_input.setStyleSheet(input_style)
        professional_layout.addRow("Assurance:", self.assurance_input)
        
        self.profession_input = QLineEdit()
        self.profession_input.setPlaceholderText("Profession du patient")
        self.profession_input.setStyleSheet(input_style)
        professional_layout.addRow("Profession:", self.profession_input)
        
        form_layout.addWidget(professional_group)
        
        # Medical Information Group
        medical_group = QGroupBox("Informations Médicales")
        medical_group.setStyleSheet(personal_group.styleSheet())
        medical_layout = QFormLayout(medical_group)
        medical_layout.setSpacing(15)
        
        self.maladie_input = QLineEdit()
        self.maladie_input.setPlaceholderText("Maladies ou conditions médicales")
        self.maladie_input.setStyleSheet(input_style)
        medical_layout.addRow("Maladie:", self.maladie_input)
        
        self.observation_input = QTextEdit()
        self.observation_input.setPlaceholderText("Observations et notes sur le patient...")
        self.observation_input.setMaximumHeight(100)
        self.observation_input.setStyleSheet(input_style)
        medical_layout.addRow("Observations:", self.observation_input)
        
        form_layout.addWidget(medical_group)
        
        main_layout.addWidget(form_frame)
        
        # X-ray section (only shown in edit mode)
        self.xray_frame = QFrame()
        self.xray_frame.setStyleSheet(form_frame.styleSheet())
        self.xray_frame.setVisible(False)
        xray_layout = QVBoxLayout(self.xray_frame)
        
        xray_group = QGroupBox("Radiographie")
        xray_group.setStyleSheet(personal_group.styleSheet())
        xray_group_layout = QVBoxLayout(xray_group)
        
        # X-ray display area
        self.xray_label = QLabel("Aucune radiographie")
        self.xray_label.setAlignment(Qt.AlignCenter)
        self.xray_label.setMinimumHeight(200)
        self.xray_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
                color: #666;
            }
        """)
        xray_group_layout.addWidget(self.xray_label)
        
        # X-ray buttons
        xray_button_layout = QHBoxLayout()
        
        self.upload_xray_btn = QPushButton("📁 Télécharger Radiographie")
        self.upload_xray_btn.clicked.connect(self.upload_xray)
        self.upload_xray_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.delete_xray_btn = QPushButton("🗑 Supprimer")
        self.delete_xray_btn.clicked.connect(self.delete_xray)
        self.delete_xray_btn.setEnabled(False)
        self.delete_xray_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        xray_button_layout.addWidget(self.upload_xray_btn)
        xray_button_layout.addWidget(self.delete_xray_btn)
        xray_button_layout.addStretch()
        
        xray_group_layout.addLayout(xray_button_layout)
        xray_layout.addWidget(xray_group)
        main_layout.addWidget(self.xray_frame)
        
        # Action buttons
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        self.save_btn = QPushButton("💾 Enregistrer")
        self.save_btn.clicked.connect(self.save_patient)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.reset_btn = QPushButton("🔄 Réinitialiser")
        self.reset_btn.clicked.connect(self.clear_form)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ Annuler")
        self.cancel_btn.clicked.connect(self.cancel_form)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        # Required fields note
        note_label = QLabel("* Champs obligatoires")
        note_label.setStyleSheet("color: #f44336; font-style: italic;")
        button_layout.addWidget(note_label)
        
        main_layout.addWidget(button_frame)
        
        # Set main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
        
        # Connect Enter key to save
        for input_field in [self.nom_input, self.prenom_input, self.telephone_input, 
                           self.carte_input, self.assurance_input, self.profession_input, self.maladie_input]:
            input_field.returnPressed.connect(self.save_patient)
    
    def clear_form(self):
        """Clear all form fields for new patient"""
        self.current_patient_id = None
        self.is_edit_mode = False
        
        self.title_label.setText("Nouveau Patient")
        self.subtitle_label.setText("Remplissez les informations du patient")
        
        # Clear all input fields
        self.nom_input.clear()
        self.prenom_input.clear()
        self.date_naissance_input.setDate(QDate.currentDate().addYears(-30))
        self.telephone_input.clear()
        self.carte_input.clear()
        self.assurance_input.clear()
        self.profession_input.clear()
        self.maladie_input.clear()
        self.observation_input.clear()
        
        # Hide X-ray section for new patients
        self.xray_frame.setVisible(False)
        
        # Focus on first field
        self.nom_input.setFocus()
    
    def load_patient(self, patient_id):
        """Load patient data for editing"""
        patient = self.patient_service.get_patient_by_id(patient_id)
        if not patient:
            QMessageBox.critical(self, "Erreur", "Patient non trouvé")
            return
        
        self.current_patient_id = patient_id
        self.is_edit_mode = True
        
        self.title_label.setText(f"Modifier Patient - {patient.full_name}")
        self.subtitle_label.setText("Modifiez les informations du patient")
        
        # Fill form fields
        self.nom_input.setText(patient.nom or "")
        self.prenom_input.setText(patient.prenom or "")
        self.date_naissance_input.setDate(patient.date_naissance or QDate.currentDate().addYears(-30))
        self.telephone_input.setText(patient.telephone or "")
        self.carte_input.setText(patient.numero_carte_national or "")
        self.assurance_input.setText(patient.assurance or "")
        self.profession_input.setText(patient.profession or "")
        self.maladie_input.setText(patient.maladie or "")
        self.observation_input.setPlainText(patient.observation or "")
        
        # Show X-ray section
        self.xray_frame.setVisible(True)
        self.load_xray_image(patient)
        
        # Focus on first field
        self.nom_input.setFocus()
    
    def load_xray_image(self, patient):
        """Load and display X-ray image"""
        if patient.xray_photo:
            xray_path = self.patient_service.get_xray_path(patient.id)
            if xray_path and os.path.exists(xray_path):
                pixmap = QPixmap(xray_path)
                if not pixmap.isNull():
                    # Scale image to fit label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.xray_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.xray_label.setPixmap(scaled_pixmap)
                    self.xray_label.setText("")
                    self.delete_xray_btn.setEnabled(True)
                    return
        
        # No image or image not found
        self.xray_label.clear()
        self.xray_label.setText("Aucune radiographie")
        self.delete_xray_btn.setEnabled(False)
    
    def save_patient(self):
        """Save patient data"""
        # Validate required fields
        if not self.nom_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom est obligatoire")
            self.nom_input.setFocus()
            return
        
        if not self.prenom_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le prénom est obligatoire")
            self.prenom_input.setFocus()
            return
        
        # Prepare patient data
        patient_data = {
            'nom': self.nom_input.text().strip(),
            'prenom': self.prenom_input.text().strip(),
            'date_naissance': self.date_naissance_input.date().toPyDate(),
            'telephone': self.telephone_input.text().strip(),
            'numero_carte_national': self.carte_input.text().strip(),
            'assurance': self.assurance_input.text().strip(),
            'profession': self.profession_input.text().strip(),
            'maladie': self.maladie_input.text().strip(),
            'observation': self.observation_input.toPlainText().strip()
        }
        
        # Save patient
        if self.is_edit_mode:
            success, message = self.patient_service.update_patient(self.current_patient_id, patient_data)
            patient_id = self.current_patient_id
        else:
            success, message, patient = self.patient_service.create_patient(patient_data)
            patient_id = patient.id if patient else None
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.patient_saved.emit(patient_id)
        else:
            QMessageBox.critical(self, "Erreur", message)
    
    def cancel_form(self):
        """Cancel form and return to previous view"""
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Vous avez des modifications non sauvegardées. Voulez-vous vraiment annuler?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.form_cancelled.emit()
    
    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        # Simple check - if any field has content, consider it as changes
        return (self.nom_input.text().strip() or 
                self.prenom_input.text().strip() or
                self.date_naissance_input.date() != QDate.currentDate().addYears(-30) or
                self.telephone_input.text().strip() or
                self.carte_input.text().strip() or
                self.assurance_input.text().strip() or
                self.profession_input.text().strip() or
                self.maladie_input.text().strip() or
                self.observation_input.toPlainText().strip())
    
    def upload_xray(self):
        """Upload X-ray image"""
        if not self.is_edit_mode or not self.current_patient_id:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord enregistrer le patient")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une radiographie",
            "",
            "Images (*.png *.jpg *.jpeg);;Tous les fichiers (*)"
        )
        
        if file_path:
            success, message = self.patient_service.upload_xray(self.current_patient_id, file_path)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                # Reload the image
                patient = self.patient_service.get_patient_by_id(self.current_patient_id)
                self.load_xray_image(patient)
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def delete_xray(self):
        """Delete X-ray image"""
        if not self.is_edit_mode or not self.current_patient_id:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer la radiographie?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.patient_service.delete_xray(self.current_patient_id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                # Clear the image display
                self.xray_label.clear()
                self.xray_label.setText("Aucune radiographie")
                self.delete_xray_btn.setEnabled(False)
            else:
                QMessageBox.critical(self, "Erreur", message)
