"""
Patient detail widget for viewing patient information and visits
Replaces patient_detail.html template with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                            QSplitter, QGroupBox, QScrollArea, QMessageBox, QMenu,
                            QAction, QSizePolicy, QTabWidget, QFormLayout, QTextEdit,
                            QAbstractItemView, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QBrush
from .tooth_diagram_widget import ToothDiagramWidget
from .invoice_widget import InvoiceWidget
from ..services.tooth_service import ToothService
import os
from datetime import datetime

class PatientDetailWidget(QWidget):
    """Widget for displaying detailed patient information and visit history"""
    
    # Signals
    edit_patient_requested = pyqtSignal(int)  # Emits patient ID
    add_visit_requested = pyqtSignal(int)  # Emits patient ID
    edit_visit_requested = pyqtSignal(int)  # Emits visit ID
    tooth_diagram_requested = pyqtSignal(int)  # Emits patient ID
    create_invoice_requested = pyqtSignal(int)  # Emits patient ID
    
    def __init__(self, patient_service, visit_service, tooth_service, invoice_service=None):
        super().__init__()
        self.patient_service = patient_service
        self.visit_service = visit_service
        self.tooth_service = tooth_service
        self.invoice_service = invoice_service
        self.current_patient = None
        self.visits = []
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
        main_layout.setSpacing(15)
        
        # Header section with patient info
        self.create_patient_header(main_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Patient information and X-ray
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        self.create_patient_info_section(left_layout)
        self.create_xray_section(left_layout)
        
        left_widget.setMaximumWidth(400)
        splitter.addWidget(left_widget)
        
        # Right side - Visits
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Create tab widget for tooth diagram and visit history
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3B82F6;
            }
        """)
        
        # Tooth diagram tab
        self.tooth_diagram_widget = None
        self.tooth_tab = QWidget()
        self.tooth_tab_layout = QVBoxLayout(self.tooth_tab)
        self.tab_widget.addTab(self.tooth_tab, "🦷 Diagramme Dentaire")
        
        # Visit history tab
        self.visit_tab = QWidget()
        self.setup_visit_history_tab()
        self.tab_widget.addTab(self.visit_tab, "📋 Historique des Visites")
        
        right_layout.addWidget(self.tab_widget)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)
        
        # Set main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)
    
    def create_patient_header(self, parent_layout):
        """Create the patient header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Patient name and basic info
        info_layout = QVBoxLayout()
        
        self.patient_name_label = QLabel("Nom du Patient")
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setBold(True)
        self.patient_name_label.setFont(name_font)
        self.patient_name_label.setStyleSheet("color: #2E7D32;")
        
        self.patient_basic_info = QLabel("Informations de base")
        self.patient_basic_info.setStyleSheet("color: #666; font-size: 14px;")
        
        info_layout.addWidget(self.patient_name_label)
        info_layout.addWidget(self.patient_basic_info)
        info_layout.addStretch()
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.edit_patient_btn = QPushButton("✏ Modifier Patient")
        self.edit_patient_btn.clicked.connect(self.edit_patient)
        self.edit_patient_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.add_visit_btn = QPushButton("➕ Nouvelle Visite")
        self.add_visit_btn.clicked.connect(self.add_visit)
        self.add_visit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.create_invoice_btn = QPushButton("📄 Créer Facture")
        self.create_invoice_btn.clicked.connect(self.create_invoice)
        self.create_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        button_layout.addWidget(self.edit_patient_btn)
        button_layout.addWidget(self.add_visit_btn)
        button_layout.addWidget(self.create_invoice_btn)
        
        header_layout.addLayout(button_layout)
        parent_layout.addWidget(header_frame)
    
    def create_patient_info_section(self, parent_layout):
        """Create the patient information section"""
        info_group = QGroupBox("Informations du Patient")
        info_group.setStyleSheet("""
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
        
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)
        
        # Create labels for patient information
        self.telephone_label = QLabel()
        self.carte_label = QLabel()
        self.assurance_label = QLabel()
        self.profession_label = QLabel()
        self.maladie_label = QLabel()
        self.date_of_birth_label = QLabel()
        
        info_layout.addRow("Téléphone:", self.telephone_label)
        info_layout.addRow("Carte Nationale:", self.carte_label)
        info_layout.addRow("Assurance:", self.assurance_label)
        info_layout.addRow("Profession:", self.profession_label)
        info_layout.addRow("Maladie:", self.maladie_label)
        info_layout.addRow("Date de naissance:", self.date_of_birth_label)
        
        # Observations
        self.observations_text = QTextEdit()
        self.observations_text.setReadOnly(True)
        self.observations_text.setMaximumHeight(100)
        self.observations_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                background-color: #f9f9f9;
            }
        """)
        info_layout.addRow("Observations:", self.observations_text)
        
        parent_layout.addWidget(info_group)
    
    def create_xray_section(self, parent_layout):
        """Create the X-ray section"""
        xray_group = QGroupBox("Radiographie")
        xray_group.setStyleSheet("""
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
        
        xray_layout = QVBoxLayout(xray_group)
        
        # X-ray display
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
        xray_layout.addWidget(self.xray_label)
        
        # X-ray buttons
        xray_button_layout = QHBoxLayout()
        
        self.upload_xray_btn = QPushButton("📁 Télécharger")
        self.upload_xray_btn.clicked.connect(self.upload_xray)
        
        self.delete_xray_btn = QPushButton("🗑 Supprimer")
        self.delete_xray_btn.clicked.connect(self.delete_xray)
        self.delete_xray_btn.setEnabled(False)
        
        for btn in [self.upload_xray_btn, self.delete_xray_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
        
        self.delete_xray_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 3px;
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
        
        xray_layout.addLayout(xray_button_layout)
        parent_layout.addWidget(xray_group)
    
    def create_visits_section(self, parent_layout):
        """Create the visits section"""
        visits_group = QGroupBox("Historique des Visites")
        visits_group.setStyleSheet("""
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
        
        visits_layout = QVBoxLayout(visits_group)
        
        # Visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(7)
        self.visits_table.setHorizontalHeaderLabels([
            "Date", "Dent", "Acte", "Prix", "Payé", "Reste", "Actions"
        ])
        
        # Table styling
        self.visits_table.setStyleSheet("""
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
        self.visits_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.visits_table.setAlternatingRowColors(True)
        self.visits_table.verticalHeader().setVisible(False)
        self.visits_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.visits_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Auto-resize columns
        header = self.visits_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Dent
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Acte
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Prix
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Payé
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Reste - Fixed width
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        # Set minimum column widths to ensure visibility
        self.visits_table.setColumnWidth(0, 80)   # Date
        self.visits_table.setColumnWidth(1, 50)   # Dent
        self.visits_table.setColumnWidth(3, 80)   # Prix
        self.visits_table.setColumnWidth(4, 80)   # Payé
        self.visits_table.setColumnWidth(5, 100)  # Reste - Increased width for better visibility
        self.visits_table.setColumnWidth(6, 120)  # Actions
        
        # Table events
        self.visits_table.cellDoubleClicked.connect(self.on_visit_double_click)
        self.visits_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.visits_table.customContextMenuRequested.connect(self.show_visit_context_menu)
        
        visits_layout.addWidget(self.visits_table)
        
        # Summary section
        summary_layout = QHBoxLayout()
        
        self.total_visits_label = QLabel("Total visites: 0")
        self.total_revenue_label = QLabel("Chiffre d'affaires: 0.00 DH")
        self.total_paid_label = QLabel("Total payé: 0.00 DH")
        self.total_unpaid_label = QLabel("Total impayé: 0.00 DH")
        
        for label in [self.total_visits_label, self.total_revenue_label, 
                     self.total_paid_label, self.total_unpaid_label]:
            label.setStyleSheet("font-weight: bold; color: #2E7D32; padding: 5px;")
        
        summary_layout.addWidget(self.total_visits_label)
        summary_layout.addWidget(self.total_revenue_label)
        summary_layout.addWidget(self.total_paid_label)
        summary_layout.addWidget(self.total_unpaid_label)
        summary_layout.addStretch()
        
        visits_layout.addLayout(summary_layout)
        parent_layout.addWidget(visits_group)
    
    def setup_visit_history_tab(self):
        """Setup visit history tab"""
        visit_layout = QVBoxLayout(self.visit_tab)
        visit_layout.setSpacing(15)
        
        self.create_visits_section(visit_layout)
    
    def load_patient(self, patient_id):
        """Load patient data and visits"""
        patient = self.patient_service.get_patient_by_id(patient_id)
        if not patient:
            QMessageBox.critical(self, "Erreur", "Patient non trouvé")
            return
        
        self.current_patient = patient
        self.load_patient_info()
        self.load_xray_image()
        self.load_visits()
        self.load_tooth_diagram()
    
    def load_patient_info(self):
        """Load patient information into the UI"""
        if not self.current_patient:
            return
        
        patient = self.current_patient
        
        # Header
        self.patient_name_label.setText(patient.full_name)
        basic_info = f"ID: {patient.id}"
        if patient.telephone:
            basic_info += f" • Tél: {patient.telephone}"
        self.patient_basic_info.setText(basic_info)
        
        # Information fields
        self.telephone_label.setText(patient.telephone or "Non renseigné")
        self.carte_label.setText(patient.numero_carte_national or "Non renseigné")
        self.assurance_label.setText(patient.assurance or "Non renseigné")
        self.profession_label.setText(patient.profession or "Non renseigné")
        self.maladie_label.setText(patient.maladie or "Aucune")
        self.date_of_birth_label.setText(patient.date_naissance.strftime("%d/%m/%Y") if patient.date_naissance else "Non renseigné")
        self.observations_text.setPlainText(patient.observation or "Aucune observation")
    
    def load_xray_image(self):
        """Load and display X-ray image"""
        if not self.current_patient:
            return
        
        if self.current_patient.xray_photo:
            xray_path = self.patient_service.get_xray_path(self.current_patient.id)
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
    
    def load_visits(self):
        """Load visits for the current patient"""
        if not self.current_patient:
            return
        
        self.visits = self.visit_service.get_visits_for_patient(self.current_patient.id)
        self.populate_visits_table()
        self.update_visit_summary()
    
    def load_tooth_diagram(self):
        """Load tooth diagram for the current patient"""
        if not self.current_patient:
            return
        
        # Clear existing widgets from tooth tab layout
        while self.tooth_tab_layout.count():
            child = self.tooth_tab_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create and add tooth diagram widget
        self.tooth_diagram_widget = ToothDiagramWidget(self.tooth_service, self.current_patient.id)
        self.tooth_tab_layout.addWidget(self.tooth_diagram_widget)
    
    def populate_visits_table(self):
        """Populate the visits table"""
        self.visits_table.setRowCount(len(self.visits))
        
        for row, visit in enumerate(self.visits):
            # Date
            date_str = visit.date.strftime("%d/%m/%Y") if visit.date else ""
            self.visits_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Dent (tooth number)
            self.visits_table.setItem(row, 1, QTableWidgetItem(visit.dent or ""))
            
            # Acte
            self.visits_table.setItem(row, 2, QTableWidgetItem(visit.acte or ""))
            
            # Prix
            prix_item = QTableWidgetItem(f"{visit.prix:.2f}" if visit.prix else "0.00")
            prix_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.visits_table.setItem(row, 3, prix_item)
            
            # Payé
            paye_item = QTableWidgetItem(f"{visit.paye:.2f}" if visit.paye else "0.00")
            paye_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.visits_table.setItem(row, 4, paye_item)
            
            # Reste
            reste_value = visit.reste if visit.reste is not None else 0.0
            reste_item = QTableWidgetItem(f"{reste_value:.2f}")
            reste_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Make text bold and visible
            font = reste_item.font()
            font.setBold(True)
            font.setPointSize(10)
            reste_item.setFont(font)
            
            # Simple color coding without background - just text color
            if reste_value > 0:
                # Red text for unpaid amounts
                reste_item.setForeground(QBrush(QColor(220, 20, 20)))  # Dark red
            else:
                # Green text for paid amounts
                reste_item.setForeground(QBrush(QColor(0, 150, 0)))  # Dark green
            
            self.visits_table.setItem(row, 5, reste_item)
            
            # Actions
            actions_item = QTableWidgetItem("Modifier • Supprimer")
            actions_item.setTextAlignment(Qt.AlignCenter)
            self.visits_table.setItem(row, 6, actions_item)

    def update_visit_summary(self):
        """Update visit summary statistics"""
        if not self.visits:
            self.total_visits_label.setText("Total visites: 0")
            self.total_revenue_label.setText("Chiffre d'affaires: 0.00 DH")
            self.total_paid_label.setText("Total payé: 0.00 DH")
            self.total_unpaid_label.setText("Total impayé: 0.00 DH")
            return
        
        total_visits = len(self.visits)
        total_revenue = sum(visit.prix or 0 for visit in self.visits)
        total_paid = sum(visit.paye or 0 for visit in self.visits)
        total_unpaid = sum(visit.reste or 0 for visit in self.visits)
        
        self.total_visits_label.setText(f"Total visites: {total_visits}")
        self.total_revenue_label.setText(f"Chiffre d'affaires: {total_revenue:.2f} DH")
        self.total_paid_label.setText(f"Total payé: {total_paid:.2f} DH")
        self.total_unpaid_label.setText(f"Total impayé: {total_unpaid:.2f} DH")
    
    def edit_patient(self):
        """Edit current patient"""
        if self.current_patient:
            self.edit_patient_requested.emit(self.current_patient.id)
    
    def add_visit(self):
        """Add new visit for current patient"""
        if self.current_patient:
            self.add_visit_requested.emit(self.current_patient.id)
    
    def show_tooth_diagram(self):
        """Show tooth diagram for current patient"""
        if self.current_patient:
            self.tooth_diagram_requested.emit(self.current_patient.id)
    
    def upload_xray(self):
        """Upload X-ray image"""
        if not self.current_patient:
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une radiographie",
            "",
            "Images (*.png *.jpg *.jpeg);;Tous les fichiers (*)"
        )
        
        if file_path:
            success, message = self.patient_service.upload_xray(self.current_patient.id, file_path)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                # Reload the image
                self.load_xray_image()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def delete_xray(self):
        """Delete X-ray image"""
        if not self.current_patient:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer la radiographie?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.patient_service.delete_xray(self.current_patient.id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_xray_image()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def on_visit_double_click(self, row, column):
        """Handle double-click on visit row"""
        if row < len(self.visits):
            visit = self.visits[row]
            self.edit_visit_requested.emit(visit.id)
    
    def show_visit_context_menu(self, position):
        """Show context menu for visits table"""
        if self.visits_table.itemAt(position):
            menu = QMenu(self)
            
            edit_action = menu.addAction("✏ Modifier visite")
            pay_action = menu.addAction("💰 Marquer comme payé")
            menu.addSeparator()
            delete_action = menu.addAction("🗑 Supprimer visite")
            
            action = menu.exec_(self.visits_table.mapToGlobal(position))
            
            row = self.visits_table.rowAt(position.y())
            if row >= 0 and row < len(self.visits):
                visit = self.visits[row]
                
                if action == edit_action:
                    self.edit_visit_requested.emit(visit.id)
                elif action == pay_action:
                    self.mark_visit_as_paid(visit.id)
                elif action == delete_action:
                    self.delete_visit(visit.id)
    
    def mark_visit_as_paid(self, visit_id):
        """Mark a visit as fully paid"""
        success, message = self.visit_service.mark_visit_as_paid(visit_id)
        
        if success:
            QMessageBox.information(self, "Succès", message)
            self.load_visits()  # Refresh visits
        else:
            QMessageBox.critical(self, "Erreur", message)
    
    def delete_visit(self, visit_id):
        """Delete a visit"""
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            "Êtes-vous sûr de vouloir supprimer cette visite?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.visit_service.delete_visit(visit_id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.load_visits()  # Refresh visits
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def create_invoice(self):
        """Create invoice for the current patient"""
        if not self.current_patient:
            QMessageBox.warning(self, "Attention", "Aucun patient sélectionné.")
            return
        
        if not self.invoice_service:
            QMessageBox.warning(self, "Attention", "Service de facturation non disponible.")
            return
        
        # Create invoice dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Créer Facture - {self.current_patient.full_name}")
        dialog.setModal(True)
        dialog.resize(1000, 700)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Create invoice widget
        invoice_widget = InvoiceWidget(
            self.visit_service, 
            self.invoice_service, 
            self.current_patient.id
        )
        layout.addWidget(invoice_widget)
        
        # Connect invoice created signal
        invoice_widget.invoice_created.connect(lambda path: dialog.accept())
        
        # Show dialog
        dialog.exec_()
