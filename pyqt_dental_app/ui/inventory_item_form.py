"""
Inventory Item Form Dialog for adding and editing inventory items
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QTextEdit, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QDateEdit, QPushButton, QLabel,
                            QMessageBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, date

class InventoryItemForm(QDialog):
    """Dialog for adding or editing inventory items"""
    
    item_saved = pyqtSignal(int)  # Emitted when item is saved, passes item_id
    
    def __init__(self, inventory_service, item_id=None, parent=None):
        super().__init__(parent)
        self.inventory_service = inventory_service
        self.item_id = item_id
        self.is_edit_mode = item_id is not None
        
        self.init_ui()
        self.load_categories()
        
        if self.is_edit_mode:
            self.load_item_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        title = "Modifier l'Article" if self.is_edit_mode else "Nouvel Article"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E7D32; padding: 10px;")
        layout.addWidget(title_label)
        
        # Form sections
        self.create_basic_info_section(layout)
        self.create_stock_info_section(layout)
        self.create_pricing_section(layout)
        self.create_additional_info_section(layout)
        
        # Buttons
        self.create_buttons(layout)
    
    def create_basic_info_section(self, parent_layout):
        """Create basic information section"""
        group = QGroupBox("Informations de Base")
        form_layout = QFormLayout(group)
        
        # Name (required)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom de l'article (obligatoire)")
        form_layout.addRow("Nom *:", self.name_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Description détaillée de l'article")
        form_layout.addRow("Description:", self.description_input)
        
        # Reference
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Référence ou code SKU")
        form_layout.addRow("Référence:", self.reference_input)
        
        # Brand
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Marque du produit")
        form_layout.addRow("Marque:", self.brand_input)
        
        # Supplier
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Nom du fournisseur")
        form_layout.addRow("Fournisseur:", self.supplier_input)
        
        # Category
        self.category_combo = QComboBox()
        form_layout.addRow("Catégorie:", self.category_combo)
        
        parent_layout.addWidget(group)
    
    def create_stock_info_section(self, parent_layout):
        """Create stock information section"""
        group = QGroupBox("Informations de Stock")
        form_layout = QFormLayout(group)
        
        # Current stock
        self.current_stock_input = QSpinBox()
        self.current_stock_input.setRange(0, 99999)
        self.current_stock_input.setValue(0)
        form_layout.addRow("Stock Actuel:", self.current_stock_input)
        
        # Minimum stock
        self.minimum_stock_input = QSpinBox()
        self.minimum_stock_input.setRange(0, 9999)
        self.minimum_stock_input.setValue(5)
        form_layout.addRow("Stock Minimum:", self.minimum_stock_input)
        
        # Maximum stock
        self.maximum_stock_input = QSpinBox()
        self.maximum_stock_input.setRange(1, 99999)
        self.maximum_stock_input.setValue(100)
        form_layout.addRow("Stock Maximum:", self.maximum_stock_input)
        
        # Unit
        self.unit_input = QLineEdit()
        self.unit_input.setText("pièce")
        self.unit_input.setPlaceholderText("Unité de mesure (pièce, boîte, ml, etc.)")
        form_layout.addRow("Unité:", self.unit_input)
        
        parent_layout.addWidget(group)
    
    def create_pricing_section(self, parent_layout):
        """Create pricing section"""
        group = QGroupBox("Informations de Prix")
        form_layout = QFormLayout(group)
        
        # Unit cost
        self.unit_cost_input = QDoubleSpinBox()
        self.unit_cost_input.setRange(0.0, 99999.0)
        self.unit_cost_input.setDecimals(0)  # No decimals
        self.unit_cost_input.setSuffix("")  # No suffix
        self.unit_cost_input.setButtonSymbols(QDoubleSpinBox.NoButtons)  # Remove scroll buttons
        # Prevent scroll wheel changes
        self.unit_cost_input.wheelEvent = lambda event: None
        form_layout.addRow("Prix d'Achat (DH):", self.unit_cost_input)
        
        # Selling price
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0.0, 99999.0)
        self.selling_price_input.setDecimals(0)  # No decimals
        self.selling_price_input.setSuffix("")  # No suffix
        self.selling_price_input.setButtonSymbols(QDoubleSpinBox.NoButtons)  # Remove scroll buttons
        # Prevent scroll wheel changes
        self.selling_price_input.wheelEvent = lambda event: None
        form_layout.addRow("Prix de Vente (DH):", self.selling_price_input)
        
        parent_layout.addWidget(group)
    
    def create_additional_info_section(self, parent_layout):
        """Create additional information section"""
        group = QGroupBox("Informations Supplémentaires")
        form_layout = QFormLayout(group)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Emplacement de stockage")
        form_layout.addRow("Emplacement:", self.location_input)
        
        # Expiry date
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDate(QDate.currentDate().addYears(2))
        self.expiry_date_input.setSpecialValueText("Aucune date d'expiration")
        self.expiry_date_input.setMinimumDate(QDate.currentDate())
        form_layout.addRow("Date d'Expiration:", self.expiry_date_input)
        
        # Has expiry checkbox
        self.has_expiry_checkbox = QCheckBox("Cet article a une date d'expiration")
        self.has_expiry_checkbox.toggled.connect(self.toggle_expiry_date)
        form_layout.addRow("", self.has_expiry_checkbox)
        
        # Initially disable expiry date
        self.expiry_date_input.setEnabled(False)
        
        # Active status
        self.is_active_checkbox = QCheckBox("Article actif")
        self.is_active_checkbox.setChecked(True)
        form_layout.addRow("", self.is_active_checkbox)
        
        parent_layout.addWidget(group)
    
    def create_buttons(self, parent_layout):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        
        # Cancel button
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        # Save button
        save_text = "Mettre à Jour" if self.is_edit_mode else "Créer"
        self.save_btn = QPushButton(save_text)
        self.save_btn.clicked.connect(self.save_item)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        parent_layout.addLayout(button_layout)
    
    def load_categories(self):
        """Load categories into the combo box"""
        self.category_combo.clear()
        self.category_combo.addItem("Aucune catégorie", None)
        
        try:
            categories = self.inventory_service.get_all_categories()
            for cat_id, name, description in categories:
                self.category_combo.addItem(name, cat_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des catégories: {str(e)}")
    
    def load_item_data(self):
        """Load existing item data for editing"""
        try:
            item = self.inventory_service.get_item_by_id(self.item_id)
            if not item:
                QMessageBox.critical(self, "Erreur", "Article introuvable")
                self.reject()
                return
            
            # Basic info
            self.name_input.setText(item['name'])
            self.description_input.setPlainText(item['description'] or "")
            self.reference_input.setText(item['reference'] or "")
            self.brand_input.setText(item['brand'] or "")
            self.supplier_input.setText(item['supplier'] or "")
            
            # Set category
            if item['category_id']:
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == item['category_id']:
                        self.category_combo.setCurrentIndex(i)
                        break
            
            # Stock info
            self.current_stock_input.setValue(item['current_stock'])
            self.minimum_stock_input.setValue(item['minimum_stock'])
            self.maximum_stock_input.setValue(item['maximum_stock'])
            self.unit_input.setText(item['unit'])
            
            # Pricing
            self.unit_cost_input.setValue(item['unit_cost'])
            self.selling_price_input.setValue(item['selling_price'])
            
            # Additional info
            self.location_input.setText(item['location'] or "")
            self.is_active_checkbox.setChecked(item['is_active'])
            
            # Expiry date
            if item['expiry_date']:
                self.has_expiry_checkbox.setChecked(True)
                self.expiry_date_input.setEnabled(True)
                self.expiry_date_input.setDate(QDate.fromString(str(item['expiry_date']), "yyyy-MM-dd"))
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des données: {str(e)}")
    
    def toggle_expiry_date(self, checked):
        """Toggle expiry date input based on checkbox"""
        self.expiry_date_input.setEnabled(checked)
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Le nom de l'article est obligatoire.")
            self.name_input.setFocus()
            return False
        
        if self.minimum_stock_input.value() > self.maximum_stock_input.value():
            QMessageBox.warning(self, "Validation", "Le stock minimum ne peut pas être supérieur au stock maximum.")
            self.minimum_stock_input.setFocus()
            return False
        
        if not self.unit_input.text().strip():
            QMessageBox.warning(self, "Validation", "L'unité de mesure est obligatoire.")
            self.unit_input.setFocus()
            return False
        
        return True
    
    def save_item(self):
        """Save the item"""
        if not self.validate_form():
            return
        
        try:
            # Prepare data
            item_data = {
                'name': self.name_input.text().strip(),
                'description': self.description_input.toPlainText().strip(),
                'reference': self.reference_input.text().strip(),
                'brand': self.brand_input.text().strip(),
                'supplier': self.supplier_input.text().strip(),
                'current_stock': self.current_stock_input.value(),
                'minimum_stock': self.minimum_stock_input.value(),
                'maximum_stock': self.maximum_stock_input.value(),
                'unit': self.unit_input.text().strip(),
                'unit_cost': self.unit_cost_input.value(),
                'selling_price': self.selling_price_input.value(),
                'category_id': self.category_combo.currentData(),
                'location': self.location_input.text().strip(),
                'is_active': self.is_active_checkbox.isChecked()
            }
            
            # Handle expiry date
            if self.has_expiry_checkbox.isChecked():
                expiry_date = self.expiry_date_input.date().toPyDate()
                item_data['expiry_date'] = expiry_date
            else:
                item_data['expiry_date'] = None
            
            # Save or update
            if self.is_edit_mode:
                success = self.inventory_service.update_item(self.item_id, **item_data)
                if success:
                    QMessageBox.information(self, "Succès", "Article mis à jour avec succès.")
                    self.item_saved.emit(self.item_id)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Erreur", "Erreur lors de la mise à jour de l'article.")
            else:
                item_id = self.inventory_service.create_item(**item_data)
                if item_id:
                    QMessageBox.information(self, "Succès", "Article créé avec succès.")
                    self.item_saved.emit(item_id)
                    self.accept()
                else:
                    QMessageBox.critical(self, "Erreur", "Erreur lors de la création de l'article.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
