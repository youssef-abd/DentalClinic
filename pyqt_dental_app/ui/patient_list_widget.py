"""
Patient list widget for displaying and managing patients
Replaces index.html template with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QPushButton, QLabel,
                            QMessageBox, QHeaderView, QAbstractItemView, QMenu,
                            QFrame, QSplitter, QTextEdit, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor
import sys

class PatientListWidget(QWidget):
    """Widget for displaying and managing the list of patients"""
    
    # Signals
    patient_selected = pyqtSignal(int)  # Emits patient ID
    edit_patient_requested = pyqtSignal(int)  # Emits patient ID
    add_visit_requested = pyqtSignal(int)  # Emits patient ID
    
    def __init__(self, patient_service):
        super().__init__()
        self.patient_service = patient_service
        self.patients = []
        self.filtered_patients = []
        self.init_ui()
        self.load_patients()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("Liste des Patients")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")
        
        # Search section
        search_layout = QHBoxLayout()
        search_label = QLabel("Rechercher:")
        search_label.setStyleSheet("font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom, prénom, téléphone ou numéro de carte...")
        self.search_input.textChanged.connect(self.filter_patients)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        self.clear_search_btn = QPushButton("Effacer")
        self.clear_search_btn.clicked.connect(self.clear_search)
        self.clear_search_btn.setStyleSheet("""
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
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_search_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addLayout(search_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.add_patient_btn = QPushButton("➕ Nouveau Patient")
        self.add_patient_btn.clicked.connect(self.add_patient)
        self.add_patient_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 Actualiser")
        self.refresh_btn.clicked.connect(self.refresh_patients)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        button_layout.addWidget(self.add_patient_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        
        # Patient count label
        self.count_label = QLabel()
        self.count_label.setStyleSheet("font-weight: bold; color: #666;")
        button_layout.addWidget(self.count_label)
        
        header_layout.addLayout(button_layout)
        layout.addWidget(header_frame)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Patient table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Téléphone", "Assurance", "Actions"
        ])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #e0e0e0;
                selection-background-color: #E8F5E8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableWidget::item:selected {
                background-color: #E8F5E8;
                color: #2E7D32;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Auto-resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Prénom
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Téléphone
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Assurance
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        # Table events
        self.table.cellDoubleClicked.connect(self.on_patient_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        splitter.addWidget(self.table)
        
        # Patient details panel (right side)
        details_frame = QFrame()
        details_frame.setMaximumWidth(300)
        details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        
        details_title = QLabel("Détails du Patient")
        details_title.setFont(QFont("Arial", 12, QFont.Bold))
        details_title.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")
        details_layout.addWidget(details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                background-color: #f9f9f9;
            }
        """)
        details_layout.addWidget(self.details_text)
        
        # Quick actions
        actions_group = QGroupBox("Actions Rapides")
        actions_layout = QVBoxLayout(actions_group)
        
        self.view_details_btn = QPushButton("👁 Voir Détails")
        self.view_details_btn.clicked.connect(self.view_patient_details)
        self.view_details_btn.setEnabled(False)
        
        self.edit_patient_btn = QPushButton("✏ Modifier")
        self.edit_patient_btn.clicked.connect(self.edit_patient)
        self.edit_patient_btn.setEnabled(False)
        
        self.add_visit_btn = QPushButton("➕ Nouvelle Visite")
        self.add_visit_btn.clicked.connect(self.add_visit)
        self.add_visit_btn.setEnabled(False)
        
        self.delete_patient_btn = QPushButton("🗑 Supprimer")
        self.delete_patient_btn.clicked.connect(self.delete_patient)
        self.delete_patient_btn.setEnabled(False)
        self.delete_patient_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        for btn in [self.view_details_btn, self.edit_patient_btn, self.add_visit_btn, self.delete_patient_btn]:
            btn.setStyleSheet(btn.styleSheet() + """
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
            actions_layout.addWidget(btn)
        
        details_layout.addWidget(actions_group)
        details_layout.addStretch()
        
        splitter.addWidget(details_frame)
        splitter.setSizes([800, 300])
        
        layout.addWidget(splitter)
        
        # Connect table selection
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_patients(self):
        """Load patients from database"""
        try:
            self.patients = self.patient_service.get_all_patients()
            self.filtered_patients = self.patients.copy()
            self.populate_table()
            self.update_count_label()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des patients: {str(e)}")
    
    def populate_table(self):
        """Populate the table with patient data"""
        self.table.setRowCount(len(self.filtered_patients))
        
        for row, patient in enumerate(self.filtered_patients):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(patient.id)))
            
            # Nom
            self.table.setItem(row, 1, QTableWidgetItem(patient.nom or ""))
            
            # Prénom
            self.table.setItem(row, 2, QTableWidgetItem(patient.prenom or ""))
            
            # Téléphone
            self.table.setItem(row, 3, QTableWidgetItem(patient.telephone or ""))
            
            # Assurance
            self.table.setItem(row, 4, QTableWidgetItem(patient.assurance or ""))
            
            # Actions (placeholder)
            actions_item = QTableWidgetItem("Voir • Modifier")
            actions_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, actions_item)
    
    def filter_patients(self):
        """Filter patients based on search input"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            self.filtered_patients = self.patients.copy()
        else:
            search_text = search_text.lower()
            self.filtered_patients = [
                patient for patient in self.patients
                if (search_text in (patient.nom or "").lower() or
                    search_text in (patient.prenom or "").lower() or
                    search_text in (patient.telephone or "").lower() or
                    search_text in (patient.numero_carte_national or "").lower())
            ]
        
        self.populate_table()
        self.update_count_label()
    
    def clear_search(self):
        """Clear search input"""
        self.search_input.clear()
    
    def update_count_label(self):
        """Update the patient count label"""
        total = len(self.patients)
        filtered = len(self.filtered_patients)
        
        if filtered == total:
            self.count_label.setText(f"Total: {total} patients")
        else:
            self.count_label.setText(f"Affichés: {filtered} / {total} patients")
    
    def refresh_patients(self):
        """Refresh the patient list"""
        self.load_patients()
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        # Enable/disable action buttons
        self.view_details_btn.setEnabled(has_selection)
        self.edit_patient_btn.setEnabled(has_selection)
        self.add_visit_btn.setEnabled(has_selection)
        self.delete_patient_btn.setEnabled(has_selection)
        
        if has_selection:
            row = selected_rows[0].row()
            patient = self.filtered_patients[row]
            self.show_patient_details(patient)
        else:
            self.details_text.clear()
    
    def show_patient_details(self, patient):
        """Show patient details in the details panel"""
        details = f"""
        <b>Nom complet:</b> {patient.full_name}<br>
        <b>Téléphone:</b> {patient.telephone or 'Non renseigné'}<br>
        <b>Carte nationale:</b> {patient.numero_carte_national or 'Non renseigné'}<br>
        <b>Assurance:</b> {patient.assurance or 'Non renseigné'}<br>
        <b>Profession:</b> {patient.profession or 'Non renseigné'}<br>
        <b>Maladie:</b> {patient.maladie or 'Aucune'}<br>
        <b>Nombre de visites:</b> {len(patient.visits)}<br>
        <b>Solde impayé:</b> {patient.total_unpaid:.2f} DH
        """
        
        if patient.observation:
            details += f"<br><br><b>Observations:</b><br>{patient.observation}"
        
        self.details_text.setHtml(details)
    
    def get_selected_patient(self):
        """Get the currently selected patient"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            return self.filtered_patients[row]
        return None
    
    def on_patient_double_click(self, row, column):
        """Handle double-click on patient row"""
        patient = self.filtered_patients[row]
        self.patient_selected.emit(patient.id)
    
    def show_context_menu(self, position):
        """Show context menu for table"""
        if self.table.itemAt(position):
            menu = QMenu(self)
            
            view_action = menu.addAction("👁 Voir détails")
            edit_action = menu.addAction("✏ Modifier")
            visit_action = menu.addAction("➕ Nouvelle visite")
            menu.addSeparator()
            delete_action = menu.addAction("🗑 Supprimer")
            
            action = menu.exec_(self.table.mapToGlobal(position))
            
            if action == view_action:
                self.view_patient_details()
            elif action == edit_action:
                self.edit_patient()
            elif action == visit_action:
                self.add_visit()
            elif action == delete_action:
                self.delete_patient()
    
    def view_patient_details(self):
        """View selected patient details"""
        patient = self.get_selected_patient()
        if patient:
            self.patient_selected.emit(patient.id)
    
    def edit_patient(self):
        """Edit selected patient"""
        patient = self.get_selected_patient()
        if patient:
            self.edit_patient_requested.emit(patient.id)
    
    def add_visit(self):
        """Add visit for selected patient"""
        patient = self.get_selected_patient()
        if patient:
            self.add_visit_requested.emit(patient.id)
    
    def add_patient(self):
        """Add new patient"""
        # This will be handled by the main window
        pass
    
    def delete_patient(self):
        """Delete selected patient"""
        patient = self.get_selected_patient()
        if not patient:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le patient {patient.full_name}?\n\n"
            "Cette action supprimera également toutes les visites associées et ne peut pas être annulée.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.patient_service.delete_patient(patient.id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.refresh_patients()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def focus_search(self):
        """Focus on search input"""
        self.search_input.setFocus()
        self.search_input.selectAll()
