"""
Invoice widget for selecting visits and creating invoices
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
                            QGroupBox, QMessageBox, QCheckBox, QAbstractItemView,
                            QProgressBar, QFileDialog, QSplitter, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont, QColor, QBrush
import os
import subprocess
from datetime import datetime

class InvoiceGenerationWorker(QObject):
    """Worker thread for invoice generation"""
    finished = pyqtSignal(str)  # Emits the file path
    error = pyqtSignal(str)     # Emits error message
    
    def __init__(self, invoice_service, visit_ids):
        super().__init__()
        self.invoice_service = invoice_service
        self.visit_ids = visit_ids
    
    def run(self):
        """Generate invoice in background thread"""
        try:
            # Create invoice data
            invoice_data = self.invoice_service.create_invoice_data(self.visit_ids)
            
            # Generate Word document
            file_path = self.invoice_service.create_word_invoice(invoice_data)
            
            self.finished.emit(file_path)
        except Exception as e:
            self.error.emit(str(e))

class InvoiceWidget(QWidget):
    """Widget for creating invoices from selected visits"""
    
    # Signals
    invoice_created = pyqtSignal(str)  # Emits the invoice file path
    
    def __init__(self, visit_service, invoice_service, patient_id):
        super().__init__()
        self.visit_service = visit_service
        self.invoice_service = invoice_service
        self.patient_id = patient_id
        self.visits = []
        self.selected_visit_ids = set()
        self.init_ui()
        self.load_visits()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Header
        self.create_header(main_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Visit selection
        left_widget = self.create_visit_selection_widget()
        splitter.addWidget(left_widget)
        
        # Right side - Invoice preview
        right_widget = self.create_invoice_preview_widget()
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])
        
        main_layout.addWidget(splitter)
        
        # Action buttons
        self.create_action_buttons(main_layout)
    
    def create_header(self, parent_layout):
        """Create header section"""
        header_group = QGroupBox("Création de Facture")
        header_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2E7D32;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        header_layout = QVBoxLayout(header_group)
        
        # Instructions
        instructions = QLabel(
            "Sélectionnez les visites à inclure dans la facture, puis cliquez sur 'Créer Facture'"
        )
        instructions.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        header_layout.addWidget(instructions)
        
        parent_layout.addWidget(header_group)
    
    def create_visit_selection_widget(self):
        """Create visit selection widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Visits table group
        visits_group = QGroupBox("Sélection des Visites")
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
        
        # Select all checkbox
        select_all_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Sélectionner tout")
        self.select_all_checkbox.stateChanged.connect(self.on_select_all_changed)
        select_all_layout.addWidget(self.select_all_checkbox)
        select_all_layout.addStretch()
        visits_layout.addLayout(select_all_layout)
        
        # Visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(6)
        self.visits_table.setHorizontalHeaderLabels([
            "Sélection", "Date", "Dent", "Acte", "Prix", "Status"
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
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Selection checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Dent
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Acte
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Prix
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        
        # Set column widths
        self.visits_table.setColumnWidth(0, 80)   # Selection checkbox
        
        visits_layout.addWidget(self.visits_table)
        
        # Summary
        self.visit_summary_label = QLabel("Aucune visite sélectionnée")
        self.visit_summary_label.setStyleSheet("font-weight: bold; color: #2E7D32; padding: 5px;")
        visits_layout.addWidget(self.visit_summary_label)
        
        layout.addWidget(visits_group)
        return widget
    
    def create_invoice_preview_widget(self):
        """Create invoice preview widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview group
        preview_group = QGroupBox("Aperçu de la Facture")
        preview_group.setStyleSheet("""
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
        
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.preview_text.setMaximumHeight(300)
        preview_layout.addWidget(self.preview_text)
        
        # Invoice totals
        self.invoice_totals_label = QLabel("Total: 0.00 DH")
        self.invoice_totals_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: #2E7D32; 
            padding: 10px;
            background-color: #E8F5E8;
            border-radius: 5px;
        """)
        preview_layout.addWidget(self.invoice_totals_label)
        
        layout.addWidget(preview_group)
        return widget
    
    def create_action_buttons(self, parent_layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        
        # Create invoice button
        self.create_invoice_btn = QPushButton("📄 Créer Facture")
        self.create_invoice_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.create_invoice_btn.clicked.connect(self.create_invoice)
        self.create_invoice_btn.setEnabled(False)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        button_layout.addWidget(self.create_invoice_btn)
        button_layout.addWidget(self.progress_bar)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def load_visits(self):
        """Load visits for the patient"""
        try:
            self.visits = self.visit_service.get_visits_for_patient(self.patient_id)
            self.populate_visits_table()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des visites: {str(e)}")
    
    def populate_visits_table(self):
        """Populate the visits table"""
        self.visits_table.setRowCount(len(self.visits))
        
        for row, visit in enumerate(self.visits):
            # Selection checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, v=visit: self.on_visit_selection_changed(v, state))
            self.visits_table.setCellWidget(row, 0, checkbox)
            
            # Date
            date_item = QTableWidgetItem(visit.date.strftime("%d/%m/%Y") if visit.date else "")
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.visits_table.setItem(row, 1, date_item)
            
            # Dent
            dent_item = QTableWidgetItem(visit.dent or "")
            dent_item.setFlags(dent_item.flags() & ~Qt.ItemIsEditable)
            self.visits_table.setItem(row, 2, dent_item)
            
            # Acte
            acte_item = QTableWidgetItem(visit.acte or "")
            acte_item.setFlags(acte_item.flags() & ~Qt.ItemIsEditable)
            self.visits_table.setItem(row, 3, acte_item)
            
            # Prix
            prix_item = QTableWidgetItem(f"{visit.prix:.2f} DH" if visit.prix else "0.00 DH")
            prix_item.setFlags(prix_item.flags() & ~Qt.ItemIsEditable)
            self.visits_table.setItem(row, 4, prix_item)
            
            # Status
            if visit.reste and visit.reste > 0:
                status = "Impayé"
                color = QColor(255, 0, 0)  # Red
            else:
                status = "Payé"
                color = QColor(0, 128, 0)  # Green
            
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_item.setForeground(QBrush(color))
            self.visits_table.setItem(row, 5, status_item)
    
    def on_select_all_changed(self, state):
        """Handle select all checkbox change"""
        for row in range(self.visits_table.rowCount()):
            checkbox = self.visits_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(state == Qt.Checked)
    
    def on_visit_selection_changed(self, visit, state):
        """Handle individual visit selection change"""
        if state == Qt.Checked:
            self.selected_visit_ids.add(visit.id)
        else:
            self.selected_visit_ids.discard(visit.id)
        
        self.update_summary()
        self.update_preview()
        self.create_invoice_btn.setEnabled(len(self.selected_visit_ids) > 0)
    
    def update_summary(self):
        """Update visit selection summary"""
        if not self.selected_visit_ids:
            self.visit_summary_label.setText("Aucune visite sélectionnée")
            return
        
        selected_visits = [v for v in self.visits if v.id in self.selected_visit_ids]
        total_price = sum(v.prix for v in selected_visits if v.prix)
        
        self.visit_summary_label.setText(
            f"{len(selected_visits)} visite(s) sélectionnée(s) - Total: {total_price:.2f} DH"
        )
    
    def update_preview(self):
        """Update invoice preview"""
        if not self.selected_visit_ids:
            self.preview_text.clear()
            self.invoice_totals_label.setText("Total: 0.00 DH")
            return
        
        try:
            # Create invoice data for preview
            invoice_data = self.invoice_service.create_invoice_data(list(self.selected_visit_ids))
            
            # Create preview text
            preview_lines = []
            preview_lines.append("=" * 50)
            preview_lines.append("APERÇU DE LA FACTURE")
            preview_lines.append("=" * 50)
            preview_lines.append(f"Numéro: {invoice_data['invoice_number']}")
            preview_lines.append(f"Date: {invoice_data['invoice_date']}")
            preview_lines.append(f"Patient: {invoice_data['patient']['name']}")
            preview_lines.append("")
            preview_lines.append("TRAITEMENTS:")
            preview_lines.append("-" * 30)
            
            for treatment in invoice_data['treatments']:
                preview_lines.append(
                    f"{treatment['treatment']} ({treatment['tooth']}) - "
                    f"Qty: {treatment['quantity']} - "
                    f"Total: {treatment['total_price']:.2f} DH"
                )
            
            preview_lines.append("")
            preview_lines.append("TOTAUX:")
            preview_lines.append("-" * 30)
            preview_lines.append(f"Sous-total: {invoice_data['totals']['subtotal']:.2f} DH")
            preview_lines.append(f"TVA (20%): {invoice_data['totals']['tax_amount']:.2f} DH")
            preview_lines.append(f"Total: {invoice_data['totals']['total']:.2f} DH")
            
            self.preview_text.setPlainText("\n".join(preview_lines))
            self.invoice_totals_label.setText(f"Total: {invoice_data['totals']['total']:.2f} DH")
            
        except Exception as e:
            self.preview_text.setPlainText(f"Erreur lors de la génération de l'aperçu: {str(e)}")
    
    def create_invoice(self):
        """Create invoice from selected visits"""
        if not self.selected_visit_ids:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins une visite.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.create_invoice_btn.setEnabled(False)
        
        # Create worker thread
        self.worker = InvoiceGenerationWorker(self.invoice_service, list(self.selected_visit_ids))
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.finished.connect(self.on_invoice_created)
        self.worker.error.connect(self.on_invoice_error)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        
        # Start thread
        self.worker_thread.start()
    
    def on_invoice_created(self, file_path):
        """Handle successful invoice creation"""
        self.progress_bar.setVisible(False)
        self.create_invoice_btn.setEnabled(True)
        
        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Facture Créée")
        msg.setText("La facture a été créée avec succès!")
        msg.setInformativeText(f"Fichier sauvegardé: {file_path}")
        
        # Add buttons
        open_btn = msg.addButton("Ouvrir", QMessageBox.ActionRole)
        open_folder_btn = msg.addButton("Ouvrir le dossier", QMessageBox.ActionRole)
        msg.addButton("OK", QMessageBox.AcceptRole)
        
        msg.exec_()
        
        # Handle button clicks
        if msg.clickedButton() == open_btn:
            self.open_file(file_path)
        elif msg.clickedButton() == open_folder_btn:
            self.open_folder(os.path.dirname(file_path))
        
        # Emit signal
        self.invoice_created.emit(file_path)
    
    def on_invoice_error(self, error_message):
        """Handle invoice creation error"""
        self.progress_bar.setVisible(False)
        self.create_invoice_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Erreur", f"Erreur lors de la création de la facture:\n{error_message}")
    
    def open_file(self, file_path):
        """Open the generated file with default application"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Attention", f"Impossible d'ouvrir le fichier: {str(e)}")
    
    def open_folder(self, folder_path):
        """Open the folder containing the file"""
        try:
            # Normalize path separators for Windows
            if os.name == 'nt':  # Windows
                folder_path = folder_path.replace('/', '\\')
                subprocess.run(['explorer', folder_path], check=True)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['xdg-open', folder_path], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Attention", f"Impossible d'ouvrir le dossier: {str(e)}") 