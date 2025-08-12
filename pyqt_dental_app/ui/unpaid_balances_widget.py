"""
Unpaid balances widget for viewing and managing unpaid visits
Replaces unpaid_balances.html template with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                            QFrame, QGroupBox, QHeaderView, QAbstractItemView, 
                            QMenu, QComboBox, QDateEdit, QLineEdit, QSizePolicy,
                            QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QBrush
from datetime import datetime, date, timedelta

class UnpaidBalancesWidget(QWidget):
    """Widget for displaying and managing unpaid visit balances"""
    
    # Signals
    patient_selected = pyqtSignal(int)  # Emits patient ID
    visit_edit_requested = pyqtSignal(int)  # Emits visit ID
    
    def __init__(self, visit_service, patient_service):
        super().__init__()
        self.visit_service = visit_service
        self.patient_service = patient_service
        self.unpaid_visits = []
        self.filtered_visits = []
        self.init_ui()
        self.load_unpaid_visits()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # Create content layout
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        title_label = QLabel("Soldes Impayés")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #f44336; margin-bottom: 10px;")
        header_layout.addWidget(title_label)
        
        # Filters section
        filters_layout = QHBoxLayout()
        
        # Date range filter
        date_label = QLabel("Période:")
        date_label.setStyleSheet("font-weight: bold;")
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_from.setCalendarPopup(True)
        self.date_from.dateChanged.connect(self.apply_filters)
        
        date_to_label = QLabel("à")
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.dateChanged.connect(self.apply_filters)
        
        # Minimum amount filter
        amount_label = QLabel("Montant min:")
        amount_label.setStyleSheet("font-weight: bold;")
        
        self.min_amount_input = QLineEdit()
        self.min_amount_input.setPlaceholderText("0.00")
        self.min_amount_input.setMaximumWidth(100)
        self.min_amount_input.textChanged.connect(self.apply_filters)
        
        # Patient search
        search_label = QLabel("Patient:")
        search_label.setStyleSheet("font-weight: bold;")
        
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("Nom du patient...")
        self.patient_search.textChanged.connect(self.apply_filters)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Effacer Filtres")
        self.clear_filters_btn.clicked.connect(self.clear_filters)
        self.clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        # Style for date and input widgets
        input_style = """
            QDateEdit, QLineEdit {
                padding: 6px;
                border: 2px solid #ddd;
                border-radius: 3px;
                font-size: 12px;
            }
            QDateEdit:focus, QLineEdit:focus {
                border-color: #4CAF50;
            }
        """
        
        for widget in [self.date_from, self.date_to, self.min_amount_input, self.patient_search]:
            widget.setStyleSheet(input_style)
        
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(date_to_label)
        filters_layout.addWidget(self.date_to)
        filters_layout.addWidget(amount_label)
        filters_layout.addWidget(self.min_amount_input)
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.patient_search)
        filters_layout.addWidget(self.clear_filters_btn)
        filters_layout.addStretch()
        
        header_layout.addLayout(filters_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Actualiser")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setStyleSheet("""
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
        
        self.export_btn = QPushButton("📊 Exporter")
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setStyleSheet("""
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
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        
        # Summary labels
        self.count_label = QLabel()
        self.total_label = QLabel()
        
        for label in [self.count_label, self.total_label]:
            label.setStyleSheet("font-weight: bold; color: #f44336; padding: 5px;")
        
        button_layout.addWidget(self.count_label)
        button_layout.addWidget(self.total_label)
        
        header_layout.addLayout(button_layout)
        layout.addWidget(header_frame, 0)  # Header frame gets no stretch
        
        # Summary section - MOVED TO TOP
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #ffebee;
                border: 1px solid #f44336;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.summary_stats = QLabel()
        self.summary_stats.setStyleSheet("font-size: 14px; font-weight: bold; color: #f44336;")
        summary_layout.addWidget(self.summary_stats)
        summary_layout.addStretch()
        
        layout.addWidget(summary_frame, 0)  # Summary frame gets no stretch
        
        # Table section
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_layout.setStretch(0, 1)  # Make table take all available space
        
        # Unpaid visits table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Patient", "Date", "Acte", "Prix", "Payé", "Reste", "Actions"
        ])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #e0e0e0;
                selection-background-color: #ffebee;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e0e0e0;
                min-height: 20px;
            }
            QTableWidget::item:selected {
                background-color: #ffebee;
                color: #f44336;
            }
            QHeaderView::section {
                background-color: #f44336;
                color: white;
                padding: 20px 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                min-height: 35px;
                text-align: center;
            }
            QHeaderView {
                background-color: #f44336;
                color: white;
                min-height: 35px;
            }
        """)
        
        # Table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Make table expand to fill available space - NO internal scrolling
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable internal vertical scroll
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set row height for better visibility
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        # Set reasonable minimum height
        self.table.setMinimumHeight(400)  # Increased minimum height for better visibility
        
        # Auto-resize columns with better visibility
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Patient
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Date - Fixed width
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Acte
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Prix - Fixed width
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Payé - Fixed width
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Reste - Fixed width
        header.setSectionResizeMode(6, QHeaderView.Fixed)    # Actions - Fixed width
        
        # Set minimum column widths to ensure visibility
        self.table.setColumnWidth(1, 120)  # Date - Increased width
        self.table.setColumnWidth(3, 120)  # Prix - Increased width
        self.table.setColumnWidth(4, 120)  # Payé - Increased width
        self.table.setColumnWidth(5, 140)  # Reste - Increased width for better visibility
        self.table.setColumnWidth(6, 250)  # Actions - Increased width for better button layout
        
        # Table events
        self.table.cellDoubleClicked.connect(self.on_row_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame, 1)  # Give table frame stretch factor of 1 to take remaining space
        
        # Set content widget to scroll area
        self.scroll_area.setWidget(self.content_widget)
        
        # Add scroll area to main layout with stretch
        main_layout.addWidget(self.scroll_area, 1)
    
    def load_unpaid_visits(self):
        """Load unpaid visits from database"""
        try:
            self.unpaid_visits = self.visit_service.get_all_unpaid_visits()
            self.filtered_visits = self.unpaid_visits.copy()
            self.populate_table()
            self.update_summary()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {str(e)}")
    
    def populate_table(self):
        """Populate the table with unpaid visits"""
        self.table.setRowCount(len(self.filtered_visits))
        
        for row, visit in enumerate(self.filtered_visits):
            # Patient name
            patient_name = visit.patient.full_name if visit.patient else "Patient inconnu"
            patient_item = QTableWidgetItem(patient_name)
            self.table.setItem(row, 0, patient_item)
            
            # Date
            date_str = visit.date.strftime("%d/%m/%Y") if visit.date else ""
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 1, date_item)
            
            # Acte
            acte_item = QTableWidgetItem(visit.acte or "")
            self.table.setItem(row, 2, acte_item)
            
            # Prix
            prix_item = QTableWidgetItem(f"{visit.prix:.2f}" if visit.prix else "0.00")
            prix_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, prix_item)
            
            # Payé
            paye_item = QTableWidgetItem(f"{visit.paye:.2f}" if visit.paye else "0.00")
            paye_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 4, paye_item)
            
            # Reste (highlighted)
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
            
            self.table.setItem(row, 5, reste_item)
            
            # Actions - Create a widget with buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 3, 5, 3)
            actions_layout.setSpacing(8)
            
            # View button
            view_btn = QPushButton("Voir")
            view_btn.setToolTip("Voir les détails du patient")
            view_btn.setFixedSize(70, 28)
            view_btn.clicked.connect(lambda checked, v=visit: self.view_patient(v.patient_id))
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
            
            # Edit button
            edit_btn = QPushButton("Modifier")
            edit_btn.setToolTip("Modifier la visite")
            edit_btn.setFixedSize(80, 28)
            edit_btn.clicked.connect(lambda checked, v=visit: self.edit_visit(v.id))
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #E65100;
                }
            """)
            
            # Pay button
            pay_btn = QPushButton("Payer")
            pay_btn.setToolTip("Marquer comme payé")
            pay_btn.setFixedSize(70, 28)
            pay_btn.clicked.connect(lambda checked, v=visit: self.mark_as_paid(v.id))
            pay_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: #2E7D32;
                }
            """)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(pay_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 6, actions_widget)
    
    def apply_filters(self):
        """Apply filters to the visits list"""
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        
        try:
            min_amount = float(self.min_amount_input.text()) if self.min_amount_input.text().strip() else 0.0
        except ValueError:
            min_amount = 0.0
        
        patient_search = self.patient_search.text().strip().lower()
        
        self.filtered_visits = []
        
        for visit in self.unpaid_visits:
            # Date filter
            if visit.date and (visit.date < date_from or visit.date > date_to):
                continue
            
            # Amount filter
            if visit.reste and visit.reste < min_amount:
                continue
            
            # Patient search filter
            if patient_search:
                patient_name = visit.patient.full_name.lower() if visit.patient else ""
                if patient_search not in patient_name:
                    continue
            
            self.filtered_visits.append(visit)
        
        self.populate_table()
        self.update_summary()
    
    def clear_filters(self):
        """Clear all filters"""
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_to.setDate(QDate.currentDate())
        self.min_amount_input.clear()
        self.patient_search.clear()
    
    def update_summary(self):
        """Update summary statistics"""
        total_visits = len(self.filtered_visits)
        total_amount = sum(visit.reste or 0 for visit in self.filtered_visits)
        
        # Update labels
        self.count_label.setText(f"Visites impayées: {total_visits}")
        self.total_label.setText(f"Montant total: {total_amount:.2f} DH")
        
        # Update detailed summary
        if total_visits > 0:
            avg_amount = total_amount / total_visits
            max_amount = max(visit.reste or 0 for visit in self.filtered_visits)
            
            # Count patients with unpaid balances
            unique_patients = len(set(visit.patient_id for visit in self.filtered_visits))
            
            summary_text = (
                f"📊 Résumé: {total_visits} visites impayées • "
                f"{unique_patients} patients concernés • "
                f"Total: {total_amount:.2f} DH • "
                f"Moyenne: {avg_amount:.2f} DH • "
                f"Maximum: {max_amount:.2f} DH"
            )
        else:
            summary_text = "✅ Aucune visite impayée trouvée avec les filtres actuels"
        
        self.summary_stats.setText(summary_text)
    
    def refresh_data(self):
        """Refresh the unpaid visits data"""
        self.load_unpaid_visits()
    
    def export_data(self):
        """Export unpaid balances to CSV"""
        if not self.filtered_visits:
            QMessageBox.information(self, "Export", "Aucune donnée à exporter")
            return
        
        from PyQt5.QtWidgets import QFileDialog
        import csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les soldes impayés",
            f"soldes_impayes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV files (*.csv);;All files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow([
                        "Patient", "Date", "Acte", "Prix", "Payé", "Reste", "Téléphone", "Assurance"
                    ])
                    
                    # Data
                    for visit in self.filtered_visits:
                        patient = visit.patient
                        writer.writerow([
                            patient.full_name if patient else "",
                            visit.date.strftime("%d/%m/%Y") if visit.date else "",
                            visit.acte or "",
                            f"{visit.prix:.2f}" if visit.prix else "0.00",
                            f"{visit.paye:.2f}" if visit.paye else "0.00",
                            f"{visit.reste:.2f}" if visit.reste else "0.00",
                            patient.telephone if patient else "",
                            patient.assurance if patient else ""
                        ])
                
                QMessageBox.information(self, "Export réussi", f"Données exportées vers:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", f"Erreur lors de l'export: {str(e)}")
    
    def get_selected_visit(self):
        """Get the currently selected visit"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.filtered_visits):
                return self.filtered_visits[row]
        return None
    
    def on_row_double_click(self, row, column):
        """Handle double-click on table row"""
        if row < len(self.filtered_visits):
            visit = self.filtered_visits[row]
            if visit.patient:
                self.patient_selected.emit(visit.patient.id)
    
    def show_context_menu(self, position):
        """Show context menu for table"""
        if self.table.itemAt(position):
            menu = QMenu(self)
            
            view_patient_action = menu.addAction("👁 Voir patient")
            edit_visit_action = menu.addAction("✏ Modifier visite")
            mark_paid_action = menu.addAction("💰 Marquer comme payé")
            add_payment_action = menu.addAction("💵 Ajouter paiement")
            
            action = menu.exec_(self.table.mapToGlobal(position))
            
            visit = self.get_selected_visit()
            if visit:
                if action == view_patient_action:
                    if visit.patient:
                        self.patient_selected.emit(visit.patient.id)
                elif action == edit_visit_action:
                    self.visit_edit_requested.emit(visit.id)
                elif action == mark_paid_action:
                    self.mark_as_paid(visit.id)
                elif action == add_payment_action:
                    self.add_payment(visit.id)
    
    def mark_as_paid(self, visit_id):
        """Mark a visit as fully paid"""
        reply = QMessageBox.question(
            self,
            "Marquer comme payé",
            "Marquer cette visite comme entièrement payée?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.visit_service.mark_visit_as_paid(visit_id)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def add_payment(self, visit_id):
        """Add a payment to a visit"""
        from PyQt5.QtWidgets import QInputDialog
        
        visit = self.visit_service.get_visit_by_id(visit_id)
        if not visit:
            return
        
        remaining = visit.reste or 0.0
        
        amount, ok = QInputDialog.getDouble(
            self,
            "Ajouter un paiement",
            f"Montant restant: {remaining:.2f} DH\nMontant à payer:",
            0.0, 0.0, remaining, 2
        )
        
        if ok and amount > 0:
            success, message = self.visit_service.add_payment(visit_id, amount)
            
            if success:
                QMessageBox.information(self, "Succès", message)
                self.refresh_data()
            else:
                QMessageBox.critical(self, "Erreur", message)
    
    def view_patient(self, patient_id):
        """View patient details"""
        self.patient_selected.emit(patient_id)
    
    def edit_visit(self, visit_id):
        """Edit visit details"""
        self.visit_edit_requested.emit(visit_id)
    

