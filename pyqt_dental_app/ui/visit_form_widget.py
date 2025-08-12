"""
Visit form widget for adding and editing visits
Replaces add_visit.html and edit_visit.html templates with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox,
                            QFrame, QGroupBox, QDateEdit, QDoubleSpinBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, date

class VisitFormWidget(QWidget):
    """Widget for adding and editing visit information"""
    
    # Signals
    visit_saved = pyqtSignal(int, int)  # Emits visit ID, patient ID
    form_cancelled = pyqtSignal()
    
    def __init__(self, visit_service, patient_service):
        super().__init__()
        self.visit_service = visit_service
        self.patient_service = patient_service
        self.current_visit_id = None
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
        self.title_label = QLabel("Nouvelle Visite")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")
        header_layout.addWidget(self.title_label)
        
        # Patient info
        self.patient_info_label = QLabel("Patient: ")
        self.patient_info_label.setStyleSheet("color: #666; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.patient_info_label)
        
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
        
        # Visit Information Group
        visit_group = QGroupBox("Informations de la Visite")
        visit_group.setStyleSheet("""
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
        visit_layout = QFormLayout(visit_group)
        visit_layout.setSpacing(15)
        
        # Input field styles
        input_style = """
            QLineEdit, QTextEdit, QDateEdit, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border-color: #4CAF50;
            }
        """
        
        # Date field
        date_label = QLabel("Date de la visite:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        visit_layout.addRow(date_label, self.date_input)
        
        # Dent field (tooth number)
        dent_label = QLabel("Dent:")
        self.dent_input = QLineEdit()
        self.dent_input.setPlaceholderText("Numéro de la dent (ex: 11, 21, 32...)")
        self.dent_input.setMaxLength(10)
        visit_layout.addRow(dent_label, self.dent_input)
        
        # Treatment/Procedure field
        acte_label = QLabel("Acte/Traitement:")
        self.acte_input = QTextEdit()
        self.acte_input.setPlaceholderText("Décrivez le traitement ou la procédure effectuée...")
        self.acte_input.setMaximumHeight(120)
        self.acte_input.setStyleSheet(input_style)
        visit_layout.addRow(acte_label, self.acte_input)
        
        form_layout.addWidget(visit_group)
        
        # Financial Information Group
        financial_group = QGroupBox("Informations Financières")
        financial_group.setStyleSheet(visit_group.styleSheet())
        financial_layout = QFormLayout(financial_group)
        financial_layout.setSpacing(15)
        
        # Price field
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0.0, 999999.0)
        self.prix_input.setDecimals(0)  # No decimals
        self.prix_input.setSuffix("")  # No suffix
        self.prix_input.setButtonSymbols(QDoubleSpinBox.NoButtons)  # Remove scroll buttons
        self.prix_input.setStyleSheet(input_style)
        self.prix_input.valueChanged.connect(self.calculate_reste)
        # Prevent scroll wheel changes
        self.prix_input.wheelEvent = lambda event: None
        financial_layout.addRow("Prix total (DH):", self.prix_input)
        
        # Paid amount field
        self.paye_input = QDoubleSpinBox()
        self.paye_input.setRange(0.0, 999999.0)
        self.paye_input.setDecimals(0)  # No decimals
        self.paye_input.setSuffix("")  # No suffix
        self.paye_input.setButtonSymbols(QDoubleSpinBox.NoButtons)  # Remove scroll buttons
        self.paye_input.setStyleSheet(input_style)
        self.paye_input.valueChanged.connect(self.calculate_reste)
        # Prevent scroll wheel changes
        self.paye_input.wheelEvent = lambda event: None
        financial_layout.addRow("Montant payé (DH):", self.paye_input)
        
        # Remaining amount (calculated)
        self.reste_label = QLabel("0 DH")
        self.reste_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        financial_layout.addRow("Montant restant:", self.reste_label)
        
        form_layout.addWidget(financial_group)
        
        main_layout.addWidget(form_frame)
        
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
        
        self.save_btn = QPushButton(" Enregistrer")
        self.save_btn.clicked.connect(self.save_visit)
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
        
        self.save_and_new_btn = QPushButton(" Enregistrer et Nouveau")
        self.save_and_new_btn.clicked.connect(self.save_and_new_visit)
        self.save_and_new_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.cancel_btn = QPushButton(" Annuler")
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
        button_layout.addWidget(self.save_and_new_btn)
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
        
        # Hide save_and_new button in edit mode initially
        self.save_and_new_btn.setVisible(False)
    
    def clear_form(self, patient_id=None):
        """Clear all form fields for new visit"""
        self.current_visit_id = None
        self.current_patient_id = patient_id
        self.is_edit_mode = False
        
        self.title_label.setText("Nouvelle Visite")
        
        # Load patient info if provided
        if patient_id:
            patient = self.patient_service.get_patient_by_id(patient_id)
            if patient:
                self.patient_info_label.setText(f"Patient: {patient.full_name} (ID: {patient.id})")
            else:
                self.patient_info_label.setText("Patient: Non trouvé")
        else:
            self.patient_info_label.setText("Patient: ")
        
        # Clear form fields
        self.date_input.setDate(QDate.currentDate())
        self.dent_input.clear()
        self.acte_input.clear()
        self.prix_input.setValue(0.0)
        self.prix_input.setSpecialValueText(" ")  # Show empty space instead of 0
        self.paye_input.setValue(0.0)
        self.paye_input.setSpecialValueText(" ")  # Show empty space instead of 0
        self.reste_label.setText(" ")  # Show empty space
        
        # Show save_and_new button for new visits
        self.save_and_new_btn.setVisible(True)
        
        # Focus on first field
        self.acte_input.setFocus()
    
    def load_visit(self, visit_id):
        """Load visit data for editing"""
        visit = self.visit_service.get_visit_by_id(visit_id)
        if not visit:
            QMessageBox.critical(self, "Erreur", "Visite non trouvée")
            return
        
        self.current_visit_id = visit_id
        self.current_patient_id = visit.patient_id
        self.is_edit_mode = True
        
        # Load patient info
        patient = self.patient_service.get_patient_by_id(visit.patient_id)
        if patient:
            self.title_label.setText(f"Modifier Visite - {patient.full_name}")
            self.patient_info_label.setText(f"Patient: {patient.full_name} (ID: {patient.id})")
        else:
            self.title_label.setText("Modifier Visite")
            self.patient_info_label.setText("Patient: Non trouvé")
        
        # Fill form fields
        if visit.date:
            self.date_input.setDate(QDate(visit.date))
        else:
            self.date_input.setDate(QDate.currentDate())
        
        self.dent_input.setText(visit.dent or "")
        self.acte_input.setPlainText(visit.acte or "")
        self.prix_input.setValue(visit.prix or 0.0)
        self.prix_input.setSpecialValueText(" ") if visit.prix == 0 else None
        self.paye_input.setValue(visit.paye or 0.0)
        self.paye_input.setSpecialValueText(" ") if visit.paye == 0 else None
        
        # Calculate and display remaining amount
        self.calculate_reste()
        
        # Hide save_and_new button in edit mode
        self.save_and_new_btn.setVisible(False)
        
        # Focus on first field
        self.acte_input.setFocus()
    
    def calculate_reste(self):
        """Calculate and update remaining amount"""
        prix = self.prix_input.value()
        paye = self.paye_input.value()
        reste = prix - paye
        
        self.reste_label.setText(f"{int(reste)} DH")
        
        # Color code the remaining amount
        if reste > 0:
            self.reste_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #f44336;
                    border-radius: 5px;
                    background-color: #ffebee;
                    color: #f44336;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        elif reste < 0:
            self.reste_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #ff9800;
                    border-radius: 5px;
                    background-color: #fff3e0;
                    color: #ff9800;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
        else:
            self.reste_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 2px solid #4caf50;
                    border-radius: 5px;
                    background-color: #e8f5e8;
                    color: #4caf50;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
    
    def validate_form(self):
        """Validate form data"""
        if not self.acte_input.toPlainText().strip():
            QMessageBox.warning(self, "Validation", "Le traitement/acte est obligatoire")
            self.acte_input.setFocus()
            return False
        
        if self.paye_input.value() > self.prix_input.value():
            reply = QMessageBox.question(
                self,
                "Montant payé supérieur",
                "Le montant payé est supérieur au prix total. Voulez-vous continuer?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.paye_input.setFocus()
                return False
        
        return True
    
    def save_visit(self):
        """Save visit data"""
        if not self.validate_form():
            return
        
        if not self.current_patient_id:
            QMessageBox.critical(self, "Erreur", "Aucun patient sélectionné")
            return
        
        # Prepare visit data
        visit_data = {
            'date': self.date_input.date().toPyDate().strftime('%Y-%m-%d'),
            'dent': self.dent_input.text().strip(),
            'acte': self.acte_input.toPlainText().strip(),
            'prix': self.prix_input.value(),
            'paye': self.paye_input.value()
        }
        
        # Save visit
        if self.is_edit_mode:
            success, message = self.visit_service.update_visit(self.current_visit_id, visit_data)
            visit_id = self.current_visit_id
        else:
            success, message, visit = self.visit_service.create_visit(self.current_patient_id, visit_data)
            visit_id = visit.id if visit else None
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.visit_saved.emit(visit_id, self.current_patient_id)
        else:
            QMessageBox.critical(self, "Erreur", message)
    
    def save_and_new_visit(self):
        """Save current visit and prepare form for new visit"""
        if not self.validate_form():
            return
        
        if not self.current_patient_id:
            QMessageBox.critical(self, "Erreur", "Aucun patient sélectionné")
            return
        
        # Prepare visit data
        visit_data = {
            'date': self.date_input.date().toPyDate().strftime('%Y-%m-%d'),
            'dent': self.dent_input.text().strip(),
            'acte': self.acte_input.toPlainText().strip(),
            'prix': self.prix_input.value(),
            'paye': self.paye_input.value()
        }
        
        # Save visit
        success, message, visit = self.visit_service.create_visit(self.current_patient_id, visit_data)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            # Clear form for new visit but keep the same patient
            patient_id = self.current_patient_id
            self.clear_form(patient_id)
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
        return (self.dent_input.text().strip() or 
                self.acte_input.toPlainText().strip() or 
                self.prix_input.value() > 0 or
                self.paye_input.value() > 0)
    
    def set_patient(self, patient_id):
        """Set the patient for this visit"""
        self.current_patient_id = patient_id
        patient = self.patient_service.get_patient_by_id(patient_id)
        if patient:
            self.patient_info_label.setText(f"Patient: {patient.full_name} (ID: {patient.id})")
        else:
            self.patient_info_label.setText("Patient: Non trouvé")
