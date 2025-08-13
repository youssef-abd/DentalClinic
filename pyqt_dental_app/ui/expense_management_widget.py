"""
Expense Management Widget
Main interface for managing dental practice expenses
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                            QComboBox, QDateEdit, QTextEdit, QMessageBox,
                            QHeaderView, QFrame, QSplitter, QTabWidget,
                            QFormLayout, QDoubleSpinBox, QCheckBox, QFileDialog,
                            QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from datetime import datetime, timedelta
import os

from ..services.expense_service import ExpenseService

class ExpenseManagementWidget(QWidget):
    """Main expense management interface"""
    
    def __init__(self, expense_service, parent=None):
        super().__init__(parent)
        self.expense_service = expense_service or ExpenseService()
        self.current_expenses = []
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Gestion des Dépenses")
        self.setMinimumSize(1200, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Gestion des Dépenses")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add expense button
        self.add_expense_btn = QPushButton("Nouvelle Dépense")
        self.add_expense_btn.setStyleSheet("""
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
        self.add_expense_btn.clicked.connect(self.show_add_expense_dialog)
        header_layout.addWidget(self.add_expense_btn)

        # Add category button
        self.add_category_btn = QPushButton("Nouvelle Catégorie")
        self.add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.add_category_btn.clicked.connect(self.show_add_category_dialog)
        header_layout.addWidget(self.add_category_btn)

        # Delete category button (same style as inventory)
        self.delete_category_btn = QPushButton("Supprimer Catégorie")
        self.delete_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53935;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #C62828;
            }
        """)
        self.delete_category_btn.clicked.connect(self.delete_selected_expense_category)
        header_layout.addWidget(self.delete_category_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filters section
        self.create_filters_section(main_layout)
        
        # Main content area - Remove the splitter to give all space to the table
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Only add the expense list panel, no more splitter
        self.create_expense_list_panel(content_layout)
        
        # Hide the details panel by default (can be shown via a button if needed)
        self.details_panel = QWidget()
        self.details_panel.setVisible(False)
        self.create_details_panel(self.details_panel)
        
        # Add a small button to toggle details
        self.toggle_details_btn = QPushButton("Afficher les détails")
        self.toggle_details_btn.setCheckable(True)
        self.toggle_details_btn.setChecked(False)
        self.toggle_details_btn.setMaximumWidth(150)
        self.toggle_details_btn.clicked.connect(self.toggle_details_panel)
        content_layout.addWidget(self.toggle_details_btn)
        content_layout.addWidget(self.details_panel)
        
        main_layout.addWidget(content_widget, stretch=1)  # Take all available space
    
    def create_filters_section(self, parent_layout):
        """Create filters section"""
        filters_frame = QFrame()
        filters_frame.setMaximumHeight(70)  # Hauteur réduite
        filters_frame.setFrameStyle(QFrame.Box)
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 6px;
            }
            QLabel {
                font-size: 11px;
                margin-right: 2px;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 3px 6px;
                font-size: 11px;
                max-width: 120px;
            }
        """)
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(4)
        
        # Recherche - plus compacte
        search_group = QFrame()
        search_layout = QHBoxLayout(search_group)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(4)
        search_layout.addWidget(QLabel("Recherche:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.setMaximumWidth(150)
        self.search_input.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.search_input)
        filters_layout.addWidget(search_group)
        
        # Période - plus compacte
        date_group = QFrame()
        date_layout = QHBoxLayout(date_group)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(4)
        date_layout.addWidget(QLabel("Période:"))
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2025, 1, 1))  # Set to 01/01/2025
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd/MM/yy")
        self.start_date.dateChanged.connect(self.filter_expenses)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("à"))
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(1))  # Set to tomorrow
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd/MM/yy")
        self.end_date.dateChanged.connect(self.filter_expenses)
        date_layout.addWidget(self.end_date)
        
        filters_layout.addWidget(date_group)
        
        # Catégorie - plus compacte
        cat_group = QFrame()
        cat_layout = QHBoxLayout(cat_group)
        cat_layout.setContentsMargins(0, 0, 0, 0)
        cat_layout.setSpacing(4)
        cat_layout.addWidget(QLabel("Catégorie:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("Toutes", None)
        self.category_filter.setMaximumWidth(120)
        self.category_filter.currentTextChanged.connect(self.filter_expenses)
        cat_layout.addWidget(self.category_filter)
        
                
        filters_layout.addWidget(cat_group)
        filters_layout.addStretch()
        
        parent_layout.addWidget(filters_frame)
    
    def toggle_details_panel(self, checked):
        """Toggle the visibility of the details panel"""
        self.details_panel.setVisible(checked)
        self.toggle_details_btn.setText("Masquer les détails" if checked else "Afficher les détails")
    
    def create_expense_list_panel(self, parent_layout):
        """Create expense list panel"""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(4)
        
        # Debug label (hidden by default, only shown when needed)
        self.debug_label = QLabel("")
        self.debug_label.setStyleSheet("color: red; font-style: italic; font-size: 10px;")
        self.debug_label.setVisible(False)  # Hidden by default
        list_layout.addWidget(self.debug_label)
        
        # Compact toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        
        # Refresh button - more compact
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Rafraîchir les données")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(refresh_btn)
        
        # Add a small spacer
        toolbar.addSpacing(10)
        
        # Add a label showing the current filter status
        self.filter_status_label = QLabel("Filtres: Toutes les dépenses")
        self.filter_status_label.setStyleSheet("font-size: 10px; color: #666;")
        toolbar.addWidget(self.filter_status_label)
        
        toolbar.addStretch()
        list_layout.addLayout(toolbar)
        
        # Table - take all available space
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(7)
        columns = ["Date", "Description", "Montant", "Catégorie", 
                  "Fournisseur", "Paiement", "Actions"]
        self.expenses_table.setHorizontalHeaderLabels(columns)
        
        # Table styling - more compact
        self.expenses_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 4px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 2px 4px;
            }
        """)
        
        # Table behavior
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expenses_table.setSelectionMode(QTableWidget.SingleSelection)
        self.expenses_table.verticalHeader().setVisible(False)
        
        # Column widths and behavior
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date (80px)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Description (takes remaining space)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount (80px)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category (100px)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Supplier (100px)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Payment (80px)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions (100px)
        
        # Set minimum column widths
        self.expenses_table.setColumnWidth(0, 80)  # Date
        self.expenses_table.setColumnWidth(2, 80)  # Amount
        self.expenses_table.setColumnWidth(5, 80)  # Payment
        
        list_layout.addWidget(self.expenses_table)
        
        # Summary row
        summary_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0.00 MAD")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: #1F2937; padding: 10px;")
        summary_layout.addStretch()
        summary_layout.addWidget(self.total_label)
        
        list_layout.addLayout(summary_layout)
        
        parent_layout.addWidget(list_widget)
    
    def create_details_panel(self, parent_widget):
        """Create details and analytics panel"""
        # Main container
        container = QVBoxLayout(parent_widget)
        container.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)  # More modern look
        tab_widget.setStyleSheet("""
            QTabBar::tab {
                padding: 6px 12px;
                margin: 0;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                background: #f5f5f5;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
        """)
        
        # Analytics tab
        analytics_tab = QWidget()
        analytics_layout = QVBoxLayout(analytics_tab)
        analytics_layout.setContentsMargins(10, 10, 10, 10)
        
        # Monthly summary
        monthly_group = QGroupBox("Résumé Mensuel")
        monthly_layout = QVBoxLayout(monthly_group)
        
        # Style for summary labels
        summary_style = """
            QLabel {
                font-size: 13px;
                padding: 6px 0;
                border-bottom: 1px solid #f0f0f0;
            }
        """
        
        self.current_month_label = QLabel("Ce mois: 0.00 MAD")
        self.current_month_label.setStyleSheet(summary_style + "font-weight: bold; color: #1a73e8;")
        
        self.last_month_label = QLabel("Mois dernier: 0.00 MAD")
        self.last_month_label.setStyleSheet(summary_style)
        
        self.year_total_label = QLabel("Total année: 0.00 MAD")
        self.year_total_label.setStyleSheet(summary_style)
        
        monthly_layout.addWidget(self.current_month_label)
        monthly_layout.addWidget(self.last_month_label)
        monthly_layout.addWidget(self.year_total_label)
        monthly_layout.addStretch()
        
        analytics_layout.addWidget(monthly_group)
        analytics_layout.addStretch()
        
        # Add tabs
        tab_widget.addTab(analytics_tab, " Analyses")
        
        # Categories tab
        categories_tab = self.create_categories_tab()
        tab_widget.addTab(categories_tab, "Catégories")
        
        # Suppliers tab
        suppliers_tab = self.create_suppliers_tab()
        tab_widget.addTab(suppliers_tab, "Fournisseurs")
        
        container.addWidget(tab_widget)
        
        # Add a small spacer at the bottom
        container.addStretch()
        
        return tab_widget
    
    def create_categories_tab(self):
        """Create categories management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add category button
        add_cat_btn = QPushButton("Nouvelle Catégorie")
        add_cat_btn.clicked.connect(self.show_add_category_dialog)
        layout.addWidget(add_cat_btn)
        
        # Categories list
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["Nom", "Description", "Actions"])
        layout.addWidget(self.categories_table)
        
        return tab
    
    def delete_selected_expense_category(self):
        """Delete currently selected expense category (discreet control)"""
        cat_id = self.category_filter.currentData()
        cat_name = self.category_filter.currentText()
        if not cat_id:
            QMessageBox.warning(self, "Suppression non valide", "Sélectionnez une catégorie spécifique à supprimer.")
            return
        if cat_name == "Sans catégorie":
            QMessageBox.warning(self, "Suppression non autorisée", "La catégorie par défaut ne peut pas être supprimée.")
            return
        reply = QMessageBox.question(
            self, "Supprimer Catégorie",
            f"Supprimer la catégorie '{cat_name}' ?\n\nLes dépenses seront réassignées à 'Sans catégorie'.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.expense_service.delete_category(cat_id)
                self.load_categories()
                # Select default after deletion and refresh list
                idx = self.category_filter.findText("Sans catégorie")
                if idx >= 0:
                    self.category_filter.setCurrentIndex(idx)
                self.load_expenses()
                QMessageBox.information(self, "Succès", f"Catégorie '{cat_name}' supprimée.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")

    def create_suppliers_tab(self):
        """Create suppliers management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add supplier button
        add_sup_btn = QPushButton("Nouveau Fournisseur")
        add_sup_btn.clicked.connect(self.show_add_supplier_dialog)
        layout.addWidget(add_sup_btn)
        
        # Suppliers list
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(4)
        self.suppliers_table.setHorizontalHeaderLabels(["Nom", "Contact", "Téléphone", "Actions"])
        layout.addWidget(self.suppliers_table)
        
        return tab
    
    def refresh_data(self):
        """Reload all data in the widget"""
        self.load_expenses()
        self.load_categories()
        self.load_suppliers()
        self.update_analytics()
    
    def load_data(self):
        """Load all data (initial load)"""
        self.refresh_data()
    
    def load_expenses(self):
        """Load expenses into table"""
        try:
            print("\n=== DEBUT load_expenses ===")

            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            # Log the exact date objects being used
            print(f"Plage de dates sélectionnée:")
            print(f"- Date de début (QDate): {self.start_date.date().toString('yyyy-MM-dd')}")
            print(f"- Date de fin (QDate): {self.end_date.date().toString('yyyy-MM-dd')}")
            print(f"- Date de début (Python): {start_date} (type: {type(start_date)})")
            print(f"- Date de fin (Python): {end_date} (type: {type(end_date)})")

            # Vérifier si les dates sont valides
            if start_date > end_date:
                print("ATTENTION: La date de début est postérieure à la date de fin!")

            # Get expenses
            print("\nAppel à get_expenses_by_date_range...")
            self.current_expenses = self.expense_service.get_expenses_by_date_range(
                start_date, end_date
            )

            print(f"\nRésultat: {len(self.current_expenses)} dépenses trouvées")
            if self.current_expenses:
                print("Dépenses trouvées (par date décroissante):")
                for i, exp in enumerate(self.current_expenses, 1):
                    print(f"  {i}. {exp.date} - {exp.description} ({exp.amount} MAD)")
            else:
                print("Aucune dépense trouvée dans cette plage de dates.")
            
            print("\nAppel à populate_expenses_table...")
            self.populate_expenses_table()
            print("=== FIN load_expenses ===\n")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n!!! Erreur lors du chargement des dépenses: {error_details}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {str(e)}\n\nDétails: {error_details}")
    
    def populate_expenses_table(self):
        """Populate expenses table"""
        print("\n=== DEBUT populate_expenses_table ===")
        print(f"Nombre de dépenses à afficher: {len(self.current_expenses)}")
        
        try:
            # Vérifier la référence à la table
            if not hasattr(self, 'expenses_table'):
                print("ERREUR: La table des dépenses n'est pas initialisée!")
                return
                
            # Réinitialiser le tableau
            print("Réinitialisation du tableau...")
            self.expenses_table.setRowCount(len(self.current_expenses))
            total = 0.0
            
            if not self.current_expenses:
                print("Aucune dépense à afficher")
                self.debug_label.setText("Aucune dépense trouvée pour la période sélectionnée")
                print("=== FIN populate_expenses_table (aucune donnée) ===\n")
                return
                
            # Afficher les détails de la première dépense pour débogage
            first_expense = self.current_expenses[0]
            print(f"Exemple de première dépense:")
            print(f"  - ID: {getattr(first_expense, 'id', 'N/A')}")
            print(f"  - Date: {getattr(first_expense, 'date', 'N/A')}")
            print(f"  - Description: {getattr(first_expense, 'description', 'N/A')}")
            print(f"  - Montant: {getattr(first_expense, 'amount', 'N/A')}")
            print(f"  - Catégorie ID: {getattr(first_expense, 'category_id', 'N/A')}")
            print(f"  - Fournisseur ID: {getattr(first_expense, 'supplier_id', 'N/A')}")
            
            print("\nDébut du traitement des dépenses...")
            for row, expense in enumerate(self.current_expenses):
                print(f"\nTraitement de la dépense {row+1}/{len(self.current_expenses)}:")
                print(f"  ID: {getattr(expense, 'id', 'N/A')}")
                print(f"  Date: {getattr(expense, 'date', 'N/A')}")
                print(f"  Description: {getattr(expense, 'description', 'N/A')}")
                
                try:
                    # Date
                    date_str = expense.date.strftime("%d/%m/%Y") if hasattr(expense, 'date') and expense.date else "N/A"
                    date_item = QTableWidgetItem(date_str)
                    self.expenses_table.setItem(row, 0, date_item)
                    print(f"  - Colonne Date: {date_str}")
                    
                    # Description
                    desc = getattr(expense, 'description', '') or ""
                    self.expenses_table.setItem(row, 1, QTableWidgetItem(desc))
                    
                    # Montant
                    amount = float(getattr(expense, 'amount', 0))
                    amount_item = QTableWidgetItem(f"{amount:.2f}")
                    amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.expenses_table.setItem(row, 2, amount_item)
                    total += amount
                    print(f"  - Colonne Montant: {amount:.2f}")
                    
                    # Catégorie
                    try:
                        category_name = expense.category.name if hasattr(expense, 'category') and expense.category else "N/A"
                        print(f"  - Catégorie: {category_name}")
                    except Exception as e:
                        print(f"  - Erreur récupération catégorie: {str(e)}")
                        category_name = "N/A"
                    self.expenses_table.setItem(row, 3, QTableWidgetItem(category_name))
                    
                    # Fournisseur
                    try:
                        supplier_name = expense.supplier.name if hasattr(expense, 'supplier') and expense.supplier else "N/A"
                        print(f"  - Fournisseur: {supplier_name}")
                    except Exception as e:
                        print(f"  - Erreur récupération fournisseur: {str(e)}")
                        supplier_name = "N/A"
                    self.expenses_table.setItem(row, 4, QTableWidgetItem(supplier_name))
                    
                    # Mode de paiement
                    payment = getattr(expense, 'payment_method', '') or ""
                    self.expenses_table.setItem(row, 5, QTableWidgetItem(payment))
                    print(f"  - Mode de paiement: {payment}")
                    
                    # Actions
                    actions_widget = self.create_actions_widget(expense)
                    self.expenses_table.setCellWidget(row, 6, actions_widget)
                    
                    print(f"  => Dépense {row+1} traitée avec succès")
                    
                except Exception as row_error:
                    import traceback
                    print(f"ERREUR lors du traitement de la ligne {row+1}: {str(row_error)}")
                    print(f"Détails: {traceback.format_exc()}")
                    continue
            
            # Mise à jour des totaux et du statut
            total_text = f"Total: {total:.2f} MAD"
            status_text = f"{len(self.current_expenses)} dépenses affichées"
            
            print(f"\nMise à jour de l'interface:")
            print(f"  - Texte du total: {total_text}")
            print(f"  - Statut: {status_text}")
            
            self.total_label.setText(total_text)
            self.debug_label.setText(status_text)
            
            # Forcer la mise à jour de l'affichage
            self.expenses_table.viewport().update()
            
            print("=== FIN populate_expenses_table (succès) ===\n")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Erreur lors du peuplement du tableau: {str(e)}"
            
            print("\n!!! ERREUR CRITIQUE !!!")
            print(error_msg)
            print(f"Détails: {error_details}")
            
            self.debug_label.setText(f"Erreur: {str(e)}")
            QMessageBox.critical(
                self, 
                "Erreur d'affichage", 
                f"Une erreur est survenue lors de l'affichage des dépenses.\n\nDétails: {str(e)}"
            )
            
            print("=== FIN populate_expenses_table (erreur) ===\n")
    
    def create_actions_widget(self, expense):
        """Create actions widget for table row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 25)
        edit_btn.setToolTip("Modifier")
        edit_btn.clicked.connect(lambda: self.edit_expense(expense))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 25)
        delete_btn.setToolTip("Supprimer")
        delete_btn.clicked.connect(lambda: self.delete_expense(expense))
        layout.addWidget(delete_btn)
        
        return widget
    
    def load_categories(self):
        """Load categories"""
        try:
            categories = self.expense_service.get_all_categories()
            
            # Update filter combo
            self.category_filter.clear()
            self.category_filter.addItem("Toutes les catégories", None)
            for category in categories:
                self.category_filter.addItem(category.name, category.id)
            
            # Update categories table
            self.categories_table.setRowCount(len(categories))
            for row, category in enumerate(categories):
                self.categories_table.setItem(row, 0, QTableWidgetItem(category.name))
                self.categories_table.setItem(row, 1, QTableWidgetItem(category.description or ""))
                
                # Actions
                actions_widget = self.create_category_actions_widget(category)
                self.categories_table.setCellWidget(row, 2, actions_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des catégories: {str(e)}")
    
    def create_category_actions_widget(self, category):
        """Create actions widget for category row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 25)
        edit_btn.clicked.connect(lambda: self.edit_category(category))
        layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 25)
        delete_btn.clicked.connect(lambda: self.delete_category(category))
        layout.addWidget(delete_btn)
        
        return widget
    
    def load_suppliers(self):
        """Load suppliers"""
        try:
            suppliers = self.expense_service.get_all_suppliers()
            
            self.suppliers_table.setRowCount(len(suppliers))
            for row, supplier in enumerate(suppliers):
                self.suppliers_table.setItem(row, 0, QTableWidgetItem(supplier.name))
                self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier.contact_person or ""))
                self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier.phone or ""))
                
                # Actions
                actions_widget = self.create_supplier_actions_widget(supplier)
                self.suppliers_table.setCellWidget(row, 3, actions_widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des fournisseurs: {str(e)}")
    
    def create_supplier_actions_widget(self, supplier):
        """Create actions widget for supplier row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 25)
        edit_btn.clicked.connect(lambda: self.edit_supplier(supplier))
        layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 25)
        delete_btn.clicked.connect(lambda: self.delete_supplier(supplier))
        layout.addWidget(delete_btn)
        
        return widget
    
    def update_analytics(self):
        """Update analytics display"""
        try:
            now = datetime.now()
            
            # Current month
            current_month_total = self.expense_service.get_monthly_expenses(now.year, now.month)
            self.current_month_label.setText(f"Ce mois: {current_month_total:.2f} MAD")
            
            # Last month
            last_month = now.replace(day=1) - timedelta(days=1)
            last_month_total = self.expense_service.get_monthly_expenses(last_month.year, last_month.month)
            self.last_month_label.setText(f"Mois dernier: {last_month_total:.2f} MAD")
            
            # Year total
            year_total = self.expense_service.get_yearly_expenses(now.year)
            self.year_total_label.setText(f"Total année: {year_total:.2f} MAD")
            
        except Exception as e:
            print(f"Error updating analytics: {e}")
    
    def filter_expenses(self):
        """Filter expenses based on current filters and search text"""
        try:
            # Get search text and convert to lowercase for case-insensitive search
            search_text = self.search_input.text().lower().strip()
            
            # Get date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            # Get current category filter
            current_category_id = self.category_filter.currentData()
            
            # Get all expenses for the date range
            all_expenses = self.expense_service.get_expenses_by_date_range(start_date, end_date)
            
            # Filter expenses based on search text and category
            filtered_expenses = []
            for expense in all_expenses:
                # Check if expense matches search text
                matches_search = True
                if search_text:
                    matches_search = (
                        search_text in (expense.description or "").lower() or
                        (expense.category and search_text in expense.category.name.lower()) or
                        (expense.supplier and search_text in expense.supplier.name.lower()) or
                        (expense.invoice_number and search_text in expense.invoice_number.lower()) or
                        (expense.payment_method and search_text in expense.payment_method.lower())
                    )
                
                # Check if expense matches category filter
                matches_category = True
                if current_category_id:
                    matches_category = (expense.category and expense.category.id == current_category_id)
                
                if matches_search and matches_category:
                    filtered_expenses.append(expense)
            
            # Update the current expenses and refresh the table
            self.current_expenses = filtered_expenses
            self.populate_expenses_table()
            
            # Update the filter status label
            status_text = f"{len(filtered_expenses)} dépenses trouvées"
            if search_text:
                status_text += f" pour la recherche '{search_text}'"
            if current_category_id:
                category_name = self.category_filter.currentText()
                status_text += f" dans la catégorie '{category_name}'"
            self.filter_status_label.setText(status_text)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error filtering expenses: {error_details}")
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue lors du filtrage des dépenses: {str(e)}")
    
    def show_add_expense_dialog(self):
        """Show add expense dialog"""
        print("\n=== DEBUT show_add_expense_dialog ===")
        print("Ouverture de la boîte de dialogue d'ajout de dépense...")
        
        try:
            from .expense_form_dialog import ExpenseFormDialog
            print("Création de la boîte de dialogue...")
            dialog = ExpenseFormDialog(self.expense_service, parent=self)
            
            print("Affichage de la boîte de dialogue...")
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                print("Utilisateur a cliqué sur Enregistrer, rechargement des données...")
                self.load_data()
                print("Données rechargées après ajout de dépense")
            else:
                print("Utilisateur a annulé l'ajout de dépense")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERREUR dans show_add_expense_dialog: {str(e)}")
            print(f"Détails: {error_details}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la dépense: {str(e)}")
            
        print("=== FIN show_add_expense_dialog ===\n")
    
    def edit_expense(self, expense):
        """Edit expense"""
        from .expense_form_dialog import ExpenseFormDialog
        dialog = ExpenseFormDialog(self.expense_service, expense, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_data()
    
    def delete_expense(self, expense):
        """Delete expense"""
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer cette dépense?\n\n{expense.description}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.expense_service.delete_expense(expense.id)
                self.load_data()
                QMessageBox.information(self, "Succès", "Dépense supprimée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def show_add_category_dialog(self):
        """Show add category dialog"""
        from .category_form_dialog import CategoryFormDialog
        dialog = CategoryFormDialog(self.expense_service, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_categories()
    
    def edit_category(self, category):
        """Edit category"""
        from .category_form_dialog import CategoryFormDialog
        dialog = CategoryFormDialog(self.expense_service, category, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_categories()
    
    def delete_category(self, category):
        """Delete category"""
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer cette catégorie?\n\n{category.name}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.expense_service.delete_category(category.id)
                self.load_categories()
                # Select default and refresh expenses so reassigned items are visible
                idx = self.category_filter.findText("Sans catégorie")
                if idx >= 0:
                    self.category_filter.setCurrentIndex(idx)
                self.load_expenses()
                QMessageBox.information(self, "Succès", "Catégorie supprimée avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def show_add_supplier_dialog(self):
        """Show add supplier dialog"""
        from .supplier_form_dialog import SupplierFormDialog
        dialog = SupplierFormDialog(self.expense_service, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_suppliers()
    
    def edit_supplier(self, supplier):
        """Edit supplier"""
        from .supplier_form_dialog import SupplierFormDialog
        dialog = SupplierFormDialog(self.expense_service, supplier, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_suppliers()
    
    def delete_supplier(self, supplier):
        """Deactivate a supplier (soft delete)"""
        reply = QMessageBox.question(
            self, "Confirmer la désactivation",
            f"Êtes-vous sûr de vouloir désactiver ce fournisseur : {supplier.name}?\n\n"
            "Le fournisseur ne sera plus sélectionnable pour de nouvelles dépenses.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.expense_service.update_supplier(supplier.id, is_active=False)
                self.load_suppliers()
                QMessageBox.information(self, "Succès", "Fournisseur désactivé avec succès!")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la désactivation: {str(e)}")
