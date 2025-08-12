"""
Inventory Management Widget for the PyQt Dental Cabinet Application
Provides comprehensive inventory management interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
                            QComboBox, QTabWidget, QGroupBox, QFormLayout,
                            QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit,
                            QMessageBox, QHeaderView, QFrame, QSplitter,
                            QProgressBar, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor, QIcon
from datetime import datetime, date
from .inventory_item_form import InventoryItemForm
import sys

class InventoryWidget(QWidget):
    """Main inventory management widget"""
    
    def __init__(self, inventory_service, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.current_item_id = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Gestion des Stocks")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Header with title and actions
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📦 Gestion des Stocks")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2E7D32; padding: 10px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Quick stats
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border: 1px solid #4CAF50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(self.stats_frame)
        
        self.total_items_label = QLabel("Articles: 0")
        self.low_stock_label = QLabel("Stock Faible: 0")
        self.expired_label = QLabel("Expirés: 0")
        self.total_value_label = QLabel("Valeur: 0.00 DH")
        
        for label in [self.total_items_label, self.low_stock_label, self.expired_label, self.total_value_label]:
            label.setFont(QFont("Arial", 10, QFont.Bold))
            stats_layout.addWidget(label)
        
        header_layout.addWidget(self.stats_frame)
        main_layout.addLayout(header_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Inventory tab
        inventory_tab = self.create_inventory_tab()
        self.tab_widget.addTab(inventory_tab, "📋 Inventaire")
        
        # Low stock tab
        low_stock_tab = self.create_low_stock_tab()
        self.tab_widget.addTab(low_stock_tab, "⚠️ Stock Faible")
        
        # Expired items tab
        expired_tab = self.create_expired_tab()
        self.tab_widget.addTab(expired_tab, "⏰ Expirés")
        
        # Transactions tab
        transactions_tab = self.create_transactions_tab()
        self.tab_widget.addTab(transactions_tab, "📊 Mouvements")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_inventory_tab(self):
        """Create the main inventory management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom, référence, marque...")
        self.search_input.textChanged.connect(self.filter_items)
        search_layout.addWidget(QLabel("Recherche:"))
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("Toutes les catégories", None)
        self.category_filter.currentTextChanged.connect(self.filter_items)
        search_layout.addWidget(QLabel("Catégorie:"))
        search_layout.addWidget(self.category_filter)
        
        # Action buttons
        self.add_item_btn = QPushButton("➕ Nouvel Article")
        self.add_item_btn.clicked.connect(self.show_add_item_dialog)
        self.add_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.create_category_btn = QPushButton("📂 Nouvelle Catégorie")
        self.create_category_btn.clicked.connect(self.show_create_category_dialog)
        self.create_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.edit_item_btn = QPushButton("✏️ Modifier")
        self.edit_item_btn.clicked.connect(self.edit_selected_item)
        self.edit_item_btn.setEnabled(False)
        
        self.delete_item_btn = QPushButton("🗑️ Supprimer")
        self.delete_item_btn.clicked.connect(self.delete_selected_item)
        self.delete_item_btn.setEnabled(False)
        
        search_layout.addWidget(self.add_item_btn)
        search_layout.addWidget(self.create_category_btn)
        search_layout.addWidget(self.edit_item_btn)
        search_layout.addWidget(self.delete_item_btn)
        
        layout.addLayout(search_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(10)
        self.items_table.setHorizontalHeaderLabels([
            "Nom", "Référence", "Marque", "Stock", "Min", "Unité", 
            "Prix Unitaire", "Catégorie", "Emplacement", "État"
        ])
        
        # Configure table
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Reference
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Brand
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Min
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Unit
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Location
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Status
        
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.itemSelectionChanged.connect(self.on_item_selected)
        self.items_table.itemDoubleClicked.connect(self.edit_selected_item)
        
        layout.addWidget(self.items_table)
        
        # Stock management section
        stock_frame = QGroupBox("Gestion des Stocks")
        stock_layout = QHBoxLayout(stock_frame)
        
        self.stock_quantity_input = QSpinBox()
        self.stock_quantity_input.setRange(1, 9999)
        self.stock_quantity_input.setValue(1)
        
        self.stock_reason_input = QLineEdit()
        self.stock_reason_input.setPlaceholderText("Motif (optionnel)")
        
        self.add_stock_btn = QPushButton("➕ Ajouter Stock")
        self.add_stock_btn.clicked.connect(self.add_stock)
        self.add_stock_btn.setEnabled(False)
        
        self.remove_stock_btn = QPushButton("➖ Retirer Stock")
        self.remove_stock_btn.clicked.connect(self.remove_stock)
        self.remove_stock_btn.setEnabled(False)
        
        stock_layout.addWidget(QLabel("Quantité:"))
        stock_layout.addWidget(self.stock_quantity_input)
        stock_layout.addWidget(QLabel("Motif:"))
        stock_layout.addWidget(self.stock_reason_input)
        stock_layout.addWidget(self.add_stock_btn)
        stock_layout.addWidget(self.remove_stock_btn)
        stock_layout.addStretch()
        
        layout.addWidget(stock_frame)
        
        return tab
    
    def create_low_stock_tab(self):
        """Create the low stock alerts tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header_label = QLabel("⚠️ Articles avec Stock Faible")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #FF6B35; padding: 10px;")
        layout.addWidget(header_label)
        
        # Low stock table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            "Nom", "Stock Actuel", "Stock Minimum", "Unité", "Fournisseur"
        ])
        
        header = self.low_stock_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.low_stock_table.setAlternatingRowColors(True)
        layout.addWidget(self.low_stock_table)
        
        return tab
    
    def create_expired_tab(self):
        """Create the expired items tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header_label = QLabel("⏰ Articles Expirés ou Expirant Bientôt")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #D32F2F; padding: 10px;")
        layout.addWidget(header_label)
        
        # Expired items table
        self.expired_table = QTableWidget()
        self.expired_table.setColumnCount(6)
        self.expired_table.setHorizontalHeaderLabels([
            "Nom", "Date d'Expiration", "Stock", "Unité", "Jours Restants", "État"
        ])
        
        header = self.expired_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.expired_table.setAlternatingRowColors(True)
        layout.addWidget(self.expired_table)
        
        return tab
    
    def create_transactions_tab(self):
        """Create the transactions history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header_label = QLabel("📊 Historique des Mouvements")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #1976D2; padding: 10px;")
        layout.addWidget(header_label)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(8)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Article", "Type", "Quantité", "Motif", "Stock Avant", "Stock Après", "Coût Total"
        ])
        
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Article name
        for i in [0, 2, 3, 4, 5, 6, 7]:
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.transactions_table.setAlternatingRowColors(True)
        layout.addWidget(self.transactions_table)
        
        return tab
    
    def load_data(self):
        """Load all data for the inventory widget"""
        self.load_categories()
        self.load_items()
        self.load_low_stock_items()
        self.load_expired_items()
        self.load_transactions()
        self.update_stats()
    
    def load_categories(self):
        """Load categories into the filter combo box"""
        self.category_filter.clear()
        self.category_filter.addItem("Toutes les catégories", None)
        
        try:
            categories = self.inventory_service.get_all_categories()
            for cat_id, name, description in categories:
                self.category_filter.addItem(name, cat_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des catégories: {str(e)}")
    
    def load_items(self):
        """Load inventory items into the table"""
        try:
            items = self.inventory_service.get_all_items()
            self.populate_items_table(items)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des articles: {str(e)}")
    
    def populate_items_table(self, items):
        """Populate the items table with data"""
        self.items_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Name
            self.items_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # Reference
            self.items_table.setItem(row, 1, QTableWidgetItem(item['reference'] or ""))
            
            # Brand
            self.items_table.setItem(row, 2, QTableWidgetItem(item['brand'] or ""))
            
            # Stock (with color coding)
            stock_item = QTableWidgetItem(str(item['current_stock']))
            if item['is_low_stock']:
                stock_item.setBackground(QColor("#FFCDD2"))  # Light red
            self.items_table.setItem(row, 3, stock_item)
            
            # Minimum stock
            self.items_table.setItem(row, 4, QTableWidgetItem(str(item['minimum_stock'])))
            
            # Unit
            self.items_table.setItem(row, 5, QTableWidgetItem(item['unit']))
            
            # Unit cost
            self.items_table.setItem(row, 6, QTableWidgetItem(f"{item['unit_cost']:.2f} DH"))
            
            # Category
            self.items_table.setItem(row, 7, QTableWidgetItem(item['category']))
            
            # Location
            self.items_table.setItem(row, 8, QTableWidgetItem(item['location'] or ""))
            
            # Status
            status = "🔴 Expiré" if item['is_expired'] else "🟡 Stock Faible" if item['is_low_stock'] else "🟢 Normal"
            self.items_table.setItem(row, 9, QTableWidgetItem(status))
            
            # Store item ID in the first column
            self.items_table.item(row, 0).setData(Qt.UserRole, item['id'])
    
    def load_low_stock_items(self):
        """Load low stock items"""
        try:
            items = self.inventory_service.get_low_stock_items()
            self.low_stock_table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                self.low_stock_table.setItem(row, 0, QTableWidgetItem(item['name']))
                self.low_stock_table.setItem(row, 1, QTableWidgetItem(str(item['current_stock'])))
                self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(item['minimum_stock'])))
                self.low_stock_table.setItem(row, 3, QTableWidgetItem(item['unit']))
                self.low_stock_table.setItem(row, 4, QTableWidgetItem(item['supplier'] or ""))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des stocks faibles: {str(e)}")
    
    def load_expired_items(self):
        """Load expired and expiring items"""
        try:
            items = self.inventory_service.get_expired_items()
            self.expired_table.setRowCount(len(items))
            
            for row, item in enumerate(items):
                self.expired_table.setItem(row, 0, QTableWidgetItem(item['name']))
                self.expired_table.setItem(row, 1, QTableWidgetItem(str(item['expiry_date'])))
                self.expired_table.setItem(row, 2, QTableWidgetItem(str(item['current_stock'])))
                self.expired_table.setItem(row, 3, QTableWidgetItem(item['unit']))
                self.expired_table.setItem(row, 4, QTableWidgetItem(str(item['days_to_expiry'])))
                
                status = "🔴 Expiré" if item['is_expired'] else "🟡 Expire Bientôt"
                status_item = QTableWidgetItem(status)
                if item['is_expired']:
                    status_item.setBackground(QColor("#FFCDD2"))  # Light red
                else:
                    status_item.setBackground(QColor("#FFF3CD"))  # Light yellow
                self.expired_table.setItem(row, 5, status_item)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des articles expirés: {str(e)}")
    
    def load_transactions(self):
        """Load transaction history"""
        try:
            transactions = self.inventory_service.get_transaction_history(limit=50)
            self.transactions_table.setRowCount(len(transactions))
            
            for row, trans in enumerate(transactions):
                self.transactions_table.setItem(row, 0, QTableWidgetItem(str(trans['transaction_date'])))
                self.transactions_table.setItem(row, 1, QTableWidgetItem(trans['item_name']))
                
                # Transaction type with icons
                type_text = {"in": "➕ Entrée", "out": "➖ Sortie", "adjustment": "⚖️ Ajustement"}
                self.transactions_table.setItem(row, 2, QTableWidgetItem(type_text.get(trans['transaction_type'], trans['transaction_type'])))
                
                self.transactions_table.setItem(row, 3, QTableWidgetItem(str(trans['quantity'])))
                self.transactions_table.setItem(row, 4, QTableWidgetItem(trans['reason'] or ""))
                self.transactions_table.setItem(row, 5, QTableWidgetItem(str(trans['stock_before'])))
                self.transactions_table.setItem(row, 6, QTableWidgetItem(str(trans['stock_after'])))
                self.transactions_table.setItem(row, 7, QTableWidgetItem(f"{trans['total_cost']:.2f} DH"))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des transactions: {str(e)}")
    
    def update_stats(self):
        """Update the statistics display"""
        try:
            # Total items
            items = self.inventory_service.get_all_items()
            self.total_items_label.setText(f"Articles: {len(items)}")
            
            # Low stock count
            low_stock = self.inventory_service.get_low_stock_items()
            self.low_stock_label.setText(f"Stock Faible: {len(low_stock)}")
            
            # Expired count
            expired = self.inventory_service.get_expired_items()
            self.expired_label.setText(f"Expirés: {len(expired)}")
            
            # Total value
            total_value = self.inventory_service.get_inventory_value()
            self.total_value_label.setText(f"Valeur: {total_value:.2f} DH")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour des statistiques: {str(e)}")
    
    def filter_items(self):
        """Filter items based on search criteria"""
        search_text = self.search_input.text().lower()
        category_id = self.category_filter.currentData()
        
        for row in range(self.items_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_text:
                name = self.items_table.item(row, 0).text().lower()
                reference = self.items_table.item(row, 1).text().lower()
                brand = self.items_table.item(row, 2).text().lower()
                
                if not (search_text in name or search_text in reference or search_text in brand):
                    show_row = False
            
            # Category filter
            if category_id is not None:
                # This would require storing category_id in the table data
                # For now, we'll filter by category name
                category_name = self.category_filter.currentText()
                item_category = self.items_table.item(row, 7).text()
                if category_name != "Toutes les catégories" and item_category != category_name:
                    show_row = False
            
            self.items_table.setRowHidden(row, not show_row)
    
    def on_item_selected(self):
        """Handle item selection in the table"""
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            item_id = self.items_table.item(current_row, 0).data(Qt.UserRole)
            self.current_item_id = item_id
            
            # Enable action buttons
            self.edit_item_btn.setEnabled(True)
            self.delete_item_btn.setEnabled(True)
            self.add_stock_btn.setEnabled(True)
            self.remove_stock_btn.setEnabled(True)
        else:
            self.current_item_id = None
            self.edit_item_btn.setEnabled(False)
            self.delete_item_btn.setEnabled(False)
            self.add_stock_btn.setEnabled(False)
            self.remove_stock_btn.setEnabled(False)
    
    def show_add_item_dialog(self):
        """Show dialog to add new item"""
        dialog = InventoryItemForm(self.inventory_service, parent=self)
        dialog.item_saved.connect(self.on_item_saved)
        dialog.exec_()
    
    def show_create_category_dialog(self):
        """Show dialog to create new category"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Nouvelle Catégorie")
        dialog.setModal(True)
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title = QLabel("Créer une nouvelle catégorie")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Nom:")
        name_label.setMinimumWidth(80)
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("Nom de la catégorie")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.category_name_input)
        layout.addLayout(name_layout)
        
        # Description field
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        self.category_desc_input = QTextEdit()
        self.category_desc_input.setPlaceholderText("Description de la catégorie (optionnel)")
        self.category_desc_input.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.category_desc_input)
        layout.addLayout(desc_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_category)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
        # Store dialog reference
        self.category_dialog = dialog
        dialog.exec_()
    
    def save_category(self):
        """Save the new category"""
        name = self.category_name_input.text().strip()
        description = self.category_desc_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom de la catégorie est obligatoire")
            return
        
        try:
            # Create the category using the inventory service
            category_id = self.inventory_service.create_category(name, description)
            
            if category_id:
                QMessageBox.information(self, "Succès", f"Catégorie '{name}' créée avec succès")
                self.category_dialog.accept()
                self.load_categories()  # Refresh the category filter
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la création de la catégorie")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création de la catégorie: {str(e)}")
    
    def edit_selected_item(self):
        """Edit the selected item"""
        if self.current_item_id:
            dialog = InventoryItemForm(self.inventory_service, self.current_item_id, parent=self)
            dialog.item_saved.connect(self.on_item_saved)
            dialog.exec_()
    
    def on_item_saved(self, item_id):
        """Handle item saved signal"""
        self.load_data()  # Refresh all data
    
    def delete_selected_item(self):
        """Delete the selected item"""
        if self.current_item_id:
            reply = QMessageBox.question(
                self, "Supprimer Article",
                "Êtes-vous sûr de vouloir supprimer cet article?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.inventory_service.delete_item(self.current_item_id)
                    self.load_data()
                    QMessageBox.information(self, "Succès", "Article supprimé avec succès")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def add_stock(self):
        """Add stock to the selected item"""
        if self.current_item_id:
            quantity = self.stock_quantity_input.value()
            reason = self.stock_reason_input.text() or "Ajout manuel"
            
            try:
                self.inventory_service.add_stock(self.current_item_id, quantity, reason=reason)
                self.load_data()
                self.stock_reason_input.clear()
                QMessageBox.information(self, "Succès", f"Stock ajouté: +{quantity}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de stock: {str(e)}")
    
    def remove_stock(self):
        """Remove stock from the selected item"""
        if self.current_item_id:
            quantity = self.stock_quantity_input.value()
            reason = self.stock_reason_input.text() or "Retrait manuel"
            
            try:
                self.inventory_service.remove_stock(self.current_item_id, quantity, reason=reason)
                self.load_data()
                self.stock_reason_input.clear()
                QMessageBox.information(self, "Succès", f"Stock retiré: -{quantity}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du retrait de stock: {str(e)}")
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_data()
