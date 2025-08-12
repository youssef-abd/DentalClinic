"""
Main window for the PyQt Dental Cabinet Application
Manages navigation between different views using QStackedWidget
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QStackedWidget, QMenuBar, QToolBar, QAction, 
                            QLabel, QStatusBar, QMessageBox, QApplication,
                            QPushButton, QFrame, QSizePolicy, QDialog)
from .dialogs.change_password_dialog import ChangePasswordDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap
# Add these imports after the existing ones
from ..sync_service import sync_service
from .sync_ui_components import SyncStatusWidget
import sys
import os

# Import expense service
from ..services.expense_service import ExpenseService

class MainWindow(QMainWindow):
    """Main application window with navigation and view management"""
    
    def __init__(self, auth_service, patient_service, visit_service, inventory_service=None):
        super().__init__()
        self.auth_service = auth_service
        self.patient_service = patient_service
        self.visit_service = visit_service
        self.inventory_service = inventory_service
        self.expense_service = ExpenseService()  # Initialize expense service
        self.current_user = None
        
        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        self.start_sync_service()
        self.add_sync_status_widget()
    
    def init_ui(self):
        """Initialize the main user interface"""
        self.setWindowTitle("DentisteDB - Gestion de Cabinet Dentaire")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #2E7D32;
                color: white;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #388E3C;
            }
            QToolBar {
                background-color: #4CAF50;
                border: none;
                spacing: 3px;
                padding: 5px;
            }
            QToolBar QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QToolBar QPushButton:hover {
                background-color: #45a049;
            }
            QToolBar QPushButton:pressed {
                background-color: #3d8b40;
            }
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #ccc;
            }
        """)
        
        # Central widget with stacked layout for different views
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget to manage different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Initialize views (will be set later)
        self.patient_list_widget = None
        self.patient_form_widget = None
        self.patient_detail_widget = None
        self.visit_form_widget = None
        self.unpaid_balances_widget = None
        self.tooth_diagram_widget = None
        self.inventory_widget = None
        self.expense_widget = None
        self.dashboard_widget = None
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('Fichier')
        
        backup_action = QAction('Sauvegarder la base de données', self)
        backup_action.setShortcut('Ctrl+B')
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Quitter', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('Affichage')
        
        dashboard_action = QAction('📊 Tableaux de Bord', self)
        dashboard_action.setShortcut('Ctrl+D')
        dashboard_action.triggered.connect(self.show_dashboards)
        view_menu.addAction(dashboard_action)
        
        view_menu.addSeparator()
        
        patient_list_action = QAction('Liste des patients', self)
        patient_list_action.setShortcut('Ctrl+P')
        patient_list_action.triggered.connect(self.show_patient_list)
        view_menu.addAction(patient_list_action)
        
        unpaid_action = QAction('Soldes impayés', self)
        unpaid_action.setShortcut('Ctrl+U')
        unpaid_action.triggered.connect(self.show_unpaid_balances)
        view_menu.addAction(unpaid_action)
        
        inventory_action = QAction('Inventaire', self)
        inventory_action.setShortcut('Ctrl+I')
        inventory_action.triggered.connect(self.show_inventory)
        view_menu.addAction(inventory_action)
        
        expenses_action = QAction('Gestion des dépenses', self)
        expenses_action.setShortcut('Ctrl+E')
        expenses_action.triggered.connect(self.show_expenses)
        view_menu.addAction(expenses_action)
        
        # Patients menu
        patients_menu = menubar.addMenu('Patients')
        
        list_patients_action = QAction('Liste des patients', self)
        list_patients_action.setShortcut('Ctrl+L')
        list_patients_action.triggered.connect(self.show_patient_list)
        patients_menu.addAction(list_patients_action)
        
        add_patient_action = QAction('Ajouter un patient', self)
        add_patient_action.setShortcut('Ctrl+N')
        add_patient_action.triggered.connect(self.show_add_patient)
        patients_menu.addAction(add_patient_action)
        
        # Visits menu
        visits_menu = menubar.addMenu('Visites')
        
        unpaid_action = QAction('Soldes impayés', self)
        unpaid_action.triggered.connect(self.show_unpaid_balances)
        visits_menu.addAction(unpaid_action)
        
        # Inventory menu
        inventory_menu = menubar.addMenu('Stocks')
        
        manage_inventory_action = QAction('📦 Gestion des Stocks', self)
        manage_inventory_action.setShortcut('Ctrl+I')
        manage_inventory_action.triggered.connect(self.show_inventory)
        inventory_menu.addAction(manage_inventory_action)
        
        low_stock_action = QAction('⚠️ Stock Faible', self)
        low_stock_action.triggered.connect(self.show_low_stock)
        inventory_menu.addAction(low_stock_action)
        
        # In the create_menu_bar method, add this to the tools_menu section:
        
        # Tools menu
        tools_menu = menubar.addMenu('Outils')
        
        search_action = QAction('Rechercher', self)
        search_action.setShortcut('Ctrl+F')
        search_action.triggered.connect(self.focus_search)
        tools_menu.addAction(search_action)
        # Add this in the tools_menu section of create_menu_bar
        # Add sync action
        sync_action = QAction('🔄 Synchroniser avec Supabase', self)
        sync_action.setShortcut('Ctrl+S')
        sync_action.triggered.connect(self.sync_to_supabase)
        tools_menu.addAction(sync_action)
        
        # Help menu
        help_menu = menubar.addMenu('Aide')
        
        about_action = QAction('À propos', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Expenses menu
        expenses_menu = menubar.addMenu('Dépenses')
        
        manage_expenses_action = QAction('💰 Gestion des Dépenses', self)
        manage_expenses_action.setShortcut('Ctrl+D')
        manage_expenses_action.triggered.connect(self.show_expenses)
        expenses_menu.addAction(manage_expenses_action)
        
        # User menu (right side)
        user_menu = menubar.addMenu('Utilisateur')
        
        change_password_action = QAction('Changer le mot de passe', self)
        change_password_action.triggered.connect(self.change_password)
        user_menu.addAction(change_password_action)
        
        user_menu.addSeparator()
        
        logout_action = QAction('Se déconnecter', self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
    
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = self.addToolBar('Navigation')
        toolbar.setMovable(False)
        
        # Dashboard button
        dashboard_btn = QPushButton('📊 Tableau de Bord')
        dashboard_btn.setToolTip('Afficher les tableaux de bord')
        dashboard_btn.clicked.connect(self.show_dashboards)
        toolbar.addWidget(dashboard_btn)
        
        # Separator
        toolbar.addSeparator()
        
        # Patient management buttons
        patients_btn = QPushButton('👥 Patients')
        patients_btn.setToolTip('Gestion des patients')
        patients_btn.clicked.connect(self.show_patient_list)
        toolbar.addWidget(patients_btn)
        
        add_patient_btn = QPushButton('➕ Nouveau Patient')
        add_patient_btn.setToolTip('Ajouter un nouveau patient')
        add_patient_btn.clicked.connect(self.show_add_patient)
        toolbar.addWidget(add_patient_btn)
        
        # Separator
        toolbar.addSeparator()
        
        # Financial buttons
        unpaid_btn = QPushButton('💰 Impayés')
        unpaid_btn.setToolTip('Voir les soldes impayés')
        unpaid_btn.clicked.connect(self.show_unpaid_balances)
        toolbar.addWidget(unpaid_btn)
        
        expenses_btn = QPushButton('💸 Dépenses')
        expenses_btn.setToolTip('Gestion des dépenses')
        expenses_btn.clicked.connect(self.show_expenses)
        toolbar.addWidget(expenses_btn)
        
        # Separator
        toolbar.addSeparator()
        
        # Inventory button
        inventory_btn = QPushButton('📦 Inventaire')
        inventory_btn.setToolTip('Gestion de l\'inventaire')
        inventory_btn.clicked.connect(self.show_inventory)
        toolbar.addWidget(inventory_btn)
        
        # Add this in the create_toolbar method, before the spacer
        # Separator
        toolbar.addSeparator()
        
        # Sync button
        sync_btn = QPushButton('🔄 Synchroniser')
        sync_btn.setToolTip('Synchroniser avec Supabase')
        sync_btn.clicked.connect(self.sync_to_supabase)
        toolbar.addWidget(sync_btn)
        
        # Add stretch to push user info to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        # User info label
        self.user_label = QLabel()
        self.user_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        toolbar.addWidget(self.user_label)
        
        logout_btn = QPushButton('🚪 Déconnexion')
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Prêt")
        self.status_bar.addWidget(self.status_label)
        
        # Add permanent widgets to the right
        self.status_bar.addPermanentWidget(QLabel("DentisteDB v1.0"))
    
    def set_current_user(self, user):
        """Set the current authenticated user"""
        self.current_user = user
        if user:
            self.user_label.setText(f"Connecté: {user.username}")
            self.status_label.setText(f"Connecté en tant que {user.username}")
    
    def add_view(self, widget, name):
        """Add a view to the stacked widget"""
        index = self.stacked_widget.addWidget(widget)
        return index
    
    def show_view(self, index):
        """Show a specific view by index"""
        self.stacked_widget.setCurrentIndex(index)
    
    def show_patient_list(self):
        """Show the patient list view"""
        if hasattr(self, 'patient_list_index'):
            self.show_view(self.patient_list_index)
            # Refresh the patient list
            if self.patient_list_widget:
                self.patient_list_widget.refresh_patients()
    
    def show_add_patient(self):
        """Show the add patient form"""
        if hasattr(self, 'patient_form_index'):
            self.show_view(self.patient_form_index)
            # Clear the form for new patient
            if self.patient_form_widget:
                self.patient_form_widget.clear_form()
    
    def show_patient_detail(self, patient_id):
        """Show patient detail view"""
        if hasattr(self, 'patient_detail_index'):
            self.show_view(self.patient_detail_index)
            if self.patient_detail_widget:
                self.patient_detail_widget.load_patient(patient_id)
    
    def show_unpaid_balances(self):
        """Show unpaid balances view"""
        if hasattr(self, 'unpaid_balances_index'):
            self.show_view(self.unpaid_balances_index)
            if self.unpaid_balances_widget:
                self.unpaid_balances_widget.refresh_data()
    
    def show_inventory(self):
        """Show inventory management view"""
        if hasattr(self, 'inventory_index'):
            self.show_view(self.inventory_index)
            if self.inventory_widget:
                self.inventory_widget.refresh_data()
    
    def show_low_stock(self):
        """Show inventory management view with low stock tab active"""
        if hasattr(self, 'inventory_index'):
            self.show_view(self.inventory_index)
            if self.inventory_widget:
                self.inventory_widget.tab_widget.setCurrentIndex(1)  # Low stock tab
                self.inventory_widget.refresh_data()
                
    def show_dashboards(self):
        """Show dashboard view with real data"""
        if not hasattr(self, 'dashboard_index'):
            try:
                from .main_dashboard_widget import MainDashboardWidget
                
                # Get database session for real data
                session = None
                if hasattr(self, 'db_manager') and self.db_manager:
                    session = self.db_manager.get_session()
                    print("✅ Database session created for dashboards")
                
                self.dashboard_widget = MainDashboardWidget(
                    parent=self,
                    session=session,
                    patient_service=self.patient_service,
                    visit_service=self.visit_service,
                    expense_service=self.expense_service
                )
                self.dashboard_index = self.stacked_widget.addWidget(self.dashboard_widget)
                print("✅ Dashboard widget created with real data connection")
            except Exception as e:
                print(f"Error creating dashboard widget: {e}")
                # Create a simple error widget
                error_widget = QWidget()
                error_layout = QVBoxLayout(error_widget)
                error_label = QLabel(f"Erreur lors du chargement des tableaux de bord:\n{str(e)}")
                error_label.setStyleSheet("color: red; font-size: 16px; padding: 50px;")
                error_label.setAlignment(Qt.AlignCenter)
                error_layout.addWidget(error_label)
                self.dashboard_index = self.stacked_widget.addWidget(error_widget)
        
        self.show_view(self.dashboard_index)
        if self.dashboard_widget and hasattr(self.dashboard_widget, 'refresh_all_dashboards'):
            self.dashboard_widget.refresh_all_dashboards()
        self.update_status("Tableaux de bord affichés")
    
    def show_expenses(self):
        """Show expense management view"""
        if not hasattr(self, 'expense_index'):
            from .expense_management_widget import ExpenseManagementWidget
            self.expense_widget = ExpenseManagementWidget(expense_service=self.expense_service)
            self.expense_index = self.stacked_widget.addWidget(self.expense_widget)
        
        self.show_view(self.expense_index)
        if self.expense_widget:
            self.expense_widget.refresh_data()
    
    def focus_search(self):
        """Focus on search field in current view"""
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'focus_search'):
            current_widget.focus_search()
    
    def backup_database(self):
        """Create database backup"""
        try:
            from ..models.database import DatabaseManager
            db_manager = DatabaseManager()
            backup_path = db_manager.backup_database()
            
            QMessageBox.information(
                self,
                "Sauvegarde réussie",
                f"Base de données sauvegardée avec succès:\n{backup_path}"
            )
            self.status_label.setText("Sauvegarde créée avec succès")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de sauvegarde",
                f"Erreur lors de la sauvegarde:\n{str(e)}"
            )
    
    def change_password(self):
        """Show change password dialog"""
        dialog = ChangePasswordDialog(self.auth_service, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.status_label.setText("Mot de passe modifié avec succès")
        else:
            self.status_label.setText("Changement de mot de passe annulé")
    
    def logout(self):
        """Logout current user"""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Êtes-vous sûr de vouloir vous déconnecter?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.close()
            # Signal to show login window again
            self.logout_requested.emit() if hasattr(self, 'logout_requested') else None
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "À propos de DentisteDB",
            """
            <h3>DentisteDB v1.0</h3>
            <p>Système de Gestion de Cabinet Dentaire</p>
            <p>Application desktop native développée avec PyQt5</p>
            <p><b>Fonctionnalités:</b></p>
            <ul>
            <li>Gestion des patients</li>
            <li>Suivi des visites et traitements</li>
            <li>Gestion des radiographies</li>
            <li>Suivi des paiements</li>
            <li>Sauvegarde automatique</li>
            </ul>
            """
        )
    
    def start_sync_service(self):
        """Start the background sync service"""
        try:
            sync_service.start_background_sync()
            self.status_label.setText("Service de synchronisation démarré")
        except Exception as e:
            print(f"Error starting sync service: {e}")
            self.status_label.setText("Erreur: Service de synchronisation non démarré")

    def add_sync_status_widget(self):
        """Add sync status widget to the status bar"""
        try:
            self.sync_status_widget = SyncStatusWidget()
            self.status_bar.addPermanentWidget(self.sync_status_widget)
        except Exception as e:
            print(f"Error adding sync status widget: {e}")
            # Create a simple error label instead
            error_label = QLabel("Sync: Error")
            error_label.setStyleSheet("color: red;")
            self.status_bar.addPermanentWidget(error_label)

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Fermer l'application",
            "Êtes-vous sûr de vouloir fermer l'application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                sync_service.stop_background_sync()
            except Exception as e:
                print(f"Error stopping sync service: {e}")
            
            # Perform cleanup
            if self.auth_service:
                self.auth_service.logout()
            event.accept()
        else:
            event.ignore()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.setText(message)

    def sync_to_supabase(self):
        """Trigger manual synchronization with Supabase"""
        try:
            # Trigger immediate sync via the background service
            result = sync_service.sync_now()
            
            if result and result.status.value == "success":
                total_synced = result.patients_synced + result.visits_synced
                QMessageBox.information(
                    self,
                    "Synchronisation réussie",
                    f"Synchronisation terminée avec succès!\n"
                    f"Patients synchronisés: {result.patients_synced}\n"
                    f"Visites synchronisées: {result.visits_synced}\n"
                    f"Total: {total_synced} enregistrements"
                )
            elif result:
                QMessageBox.warning(
                    self,
                    "Synchronisation",
                    f"Statut de synchronisation: {result.message}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Synchronisation",
                    "Erreur: Impossible de démarrer la synchronisation"
                )
                
        except Exception as e:
            print(f"Error in sync_to_supabase: {e}")
            QMessageBox.critical(
                self,
                "Erreur de synchronisation",
                f"Erreur lors de la synchronisation:\n{str(e)}"
            )
