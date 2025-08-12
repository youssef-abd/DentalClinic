"""
Main application entry point for PyQt Dental Cabinet Application
Orchestrates the entire application flow and manages view transitions
"""

import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

# Import models and services
from .models.database import DatabaseManager
from .services.auth_service import AuthService
from .services.patient_service import PatientService
from .services.visit_service import VisitService
from .services.tooth_service import ToothService
from .services.inventory_service import InventoryService
from .services.invoice_service import InvoiceService

# Import UI components
from .ui.login_widget import LoginWidget
from .ui.main_window import MainWindow
from .ui.patient_list_widget import PatientListWidget
from .ui.patient_form_widget import PatientFormWidget
from .ui.patient_detail_widget import PatientDetailWidget
from .ui.visit_form_widget import VisitFormWidget
from .ui.unpaid_balances_widget import UnpaidBalancesWidget
from .ui.inventory_widget import InventoryWidget

class DentalApplication(QObject):
    """Main application controller"""
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.stacked_widget = None
        
        # Services
        self.db_manager = None
        self.auth_service = None
        self.patient_service = None
        self.visit_service = None
        self.tooth_service = None
        self.inventory_service = None
        self.invoice_service = None
        
        # UI Components
        self.login_widget = None
        self.main_window = None
        self.patient_list_widget = None
        self.patient_form_widget = None
        self.patient_detail_widget = None
        self.visit_form_widget = None
        self.unpaid_balances_widget = None
        self.inventory_widget = None
        
        # View indices
        self.login_index = 0
        self.main_window_index = 1
        
        self.init_application()
    
    def init_application(self):
        """Initialize the application"""
        try:
            # Initialize database and services
            self.init_database()
            self.init_services()
            
            # Initialize UI
            self.init_ui()
            
            # Setup connections
            self.setup_connections()
            
            # Run Supabase sync on startup
            try:
                from .sync_to_supabase import run_sync
                # run_sync() # Commented out to prevent automatic sync on startup
                print("Initial Supabase synchronization completed.")
            except Exception as e:
                print(f"Warning: Could not perform initial sync: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(None, "Erreur d'initialisation", 
                           f"Erreur lors de l'initialisation de l'application:\n{str(e)}")
            sys.exit(1)
    
    def init_database(self):
        """Initialize database connection and create tables"""
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.create_tables()
            
            # Create default user if needed
            created = self.db_manager.init_default_user()
            if created:
                print("Utilisateur administrateur par défaut créé (mouna/123)")
                
        except Exception as e:
            raise Exception(f"Erreur de base de données: {str(e)}")
    
    def init_services(self):
        """Initialize business logic services"""
        self.auth_service = AuthService(self.db_manager)
        self.patient_service = PatientService(self.db_manager)
        self.visit_service = VisitService(self.db_manager)
        self.tooth_service = ToothService(self.db_manager)
        self.inventory_service = InventoryService(self.db_manager)
        self.invoice_service = InvoiceService(self.db_manager)
        
        # Initialize default inventory data
        try:
            self.inventory_service.init_default_data()
        except Exception as e:
            print(f"Note: Could not initialize default inventory data: {str(e)}")
    
    def init_ui(self):
        """Initialize UI components"""
        # Create main stacked widget for view management
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setWindowTitle("DentisteDB - Gestion de Cabinet Dentaire")
        self.stacked_widget.setMinimumSize(1000, 700)
        
        # Create login widget
        self.login_widget = LoginWidget(self.auth_service)
        # Center the login widget within the stacked widget
        from PyQt5.QtWidgets import QSizePolicy
        self.login_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.login_index = self.stacked_widget.addWidget(self.login_widget)
        
        # Create main window
        self.main_window = MainWindow(
            self.auth_service, 
            self.patient_service, 
            self.visit_service,
            self.inventory_service
        )
        self.main_window_index = self.stacked_widget.addWidget(self.main_window)
        
        # Create and add view widgets to main window
        self.init_main_window_views()
        
        # Start with login view
        self.stacked_widget.setCurrentIndex(self.login_index)
    
    def init_main_window_views(self):
        """Initialize and add views to the main window"""
        # Patient list widget
        self.patient_list_widget = PatientListWidget(self.patient_service)
        self.main_window.patient_list_index = self.main_window.add_view(
            self.patient_list_widget, "patient_list"
        )
        self.main_window.patient_list_widget = self.patient_list_widget
        
        # Patient form widget
        self.patient_form_widget = PatientFormWidget(self.patient_service)
        self.main_window.patient_form_index = self.main_window.add_view(
            self.patient_form_widget, "patient_form"
        )
        self.main_window.patient_form_widget = self.patient_form_widget
        
        # Patient detail widget
        self.patient_detail_widget = PatientDetailWidget(
            self.patient_service, 
            self.visit_service,
            self.tooth_service,
            self.invoice_service
        )
        self.main_window.patient_detail_index = self.main_window.add_view(
            self.patient_detail_widget, "patient_detail"
        )
        self.main_window.patient_detail_widget = self.patient_detail_widget
        
        # Visit form widget
        self.visit_form_widget = VisitFormWidget(
            self.visit_service, self.patient_service
        )
        self.main_window.visit_form_index = self.main_window.add_view(
            self.visit_form_widget, "visit_form"
        )
        self.main_window.visit_form_widget = self.visit_form_widget
        
        # Unpaid balances widget
        self.unpaid_balances_widget = UnpaidBalancesWidget(
            self.visit_service, self.patient_service
        )
        self.main_window.unpaid_balances_index = self.main_window.add_view(
            self.unpaid_balances_widget, "unpaid_balances"
        )
        self.main_window.unpaid_balances_widget = self.unpaid_balances_widget
        
        # Inventory widget
        self.inventory_widget = InventoryWidget(self.inventory_service)
        self.main_window.inventory_index = self.main_window.add_view(
            self.inventory_widget, "inventory"
        )
        self.main_window.inventory_widget = self.inventory_widget
        
        # Set default view to patient list
        self.main_window.show_patient_list()
    
    def setup_connections(self):
        """Setup signal-slot connections between components"""
        # Login widget connections
        self.login_widget.login_successful.connect(self.on_login_successful)
        
        # Main window connections
        if hasattr(self.main_window, 'logout_requested'):
            self.main_window.logout_requested.connect(self.on_logout_requested)
        
        # Patient list widget connections
        self.patient_list_widget.patient_selected.connect(self.show_patient_detail)
        self.patient_list_widget.edit_patient_requested.connect(self.edit_patient)
        self.patient_list_widget.add_visit_requested.connect(self.add_visit_for_patient)
        self.patient_list_widget.add_patient_requested.connect(self.show_add_patient)
        
        # Patient form widget connections
        self.patient_form_widget.patient_saved.connect(self.on_patient_saved)
        self.patient_form_widget.form_cancelled.connect(self.return_to_patient_list)
        
        # Patient detail widget connections
        self.patient_detail_widget.edit_patient_requested.connect(self.edit_patient)
        self.patient_detail_widget.add_visit_requested.connect(self.add_visit_for_patient)
        self.patient_detail_widget.edit_visit_requested.connect(self.edit_visit)
        self.patient_detail_widget.tooth_diagram_requested.connect(self.show_tooth_diagram)
        
        # Visit form widget connections
        self.visit_form_widget.visit_saved.connect(self.on_visit_saved)
        self.visit_form_widget.form_cancelled.connect(self.return_to_patient_detail)
        
        # Unpaid balances widget connections
        self.unpaid_balances_widget.patient_selected.connect(self.show_patient_detail)
        self.unpaid_balances_widget.visit_edit_requested.connect(self.edit_visit)
    
    def on_login_successful(self, user):
        """Handle successful login"""
        self.main_window.set_current_user(user)
        self.stacked_widget.setCurrentIndex(self.main_window_index)
        self.main_window.update_status("Connexion réussie")
        
        # Clear login form
        self.login_widget.clear_fields()
    
    def on_logout_requested(self):
        """Handle logout request"""
        self.stacked_widget.setCurrentIndex(self.login_index)
        self.login_widget.clear_fields()
    
    def show_patient_detail(self, patient_id):
        """Show patient detail view"""
        self.main_window.show_patient_detail(patient_id)
    
    def edit_patient(self, patient_id):
        """Show patient edit form"""
        self.main_window.show_view(self.main_window.patient_form_index)
        self.patient_form_widget.load_patient(patient_id)
    
    def show_add_patient(self):
        """Show add patient form"""
        self.main_window.show_view(self.main_window.patient_form_index)
        self.patient_form_widget.clear_form()
    
    def add_visit_for_patient(self, patient_id):
        """Show add visit form for specific patient"""
        self.main_window.show_view(self.main_window.visit_form_index)
        self.visit_form_widget.clear_form(patient_id)
    
    def edit_visit(self, visit_id):
        """Show edit visit form"""
        self.main_window.show_view(self.main_window.visit_form_index)
        self.visit_form_widget.load_visit(visit_id)
    
    def on_patient_saved(self, patient_id):
        """Handle patient saved event"""
        self.main_window.update_status("Patient sauvegardé avec succès")
        self.show_patient_detail(patient_id)
    
    def on_visit_saved(self, visit_id, patient_id):
        """Handle visit saved event"""
        self.main_window.update_status("Visite sauvegardée avec succès")
        self.show_patient_detail(patient_id)
    
    def return_to_patient_list(self):
        """Return to patient list view"""
        self.main_window.show_patient_list()
    
    def return_to_patient_detail(self):
        """Return to patient detail view (if we have a current patient)"""
        # This could be improved by tracking the current patient
        self.main_window.show_patient_list()
    
    def show_tooth_diagram(self, patient_id):
        """Show interactive tooth diagram for patient"""
        # This method is no longer needed as tooth diagram is embedded
        # But keep for backward compatibility
        pass
    
    def run(self):
        """Run the application"""
        self.stacked_widget.show()
        return self.app.exec_()

def setup_application():
    """Setup Qt application with proper configuration"""
    # Enable DPI awareness for Windows
    if os.name == 'nt':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass  # Older Windows versions might not support this
    
    # Set up Qt application with Windows-specific settings
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("DentisteDB")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Dental Practice Management")
    
    # Set application icon if available
    # app.setWindowIcon(QIcon("assets/icon.png"))
    
    return app

def main():
    """Main entry point"""
    try:
        # Setup Qt application
        app = setup_application()
        
        # Create and run dental application
        dental_app = DentalApplication()
        dental_app.app = app
        
        # Run the application
        exit_code = dental_app.run()
        sys.exit(exit_code)
        
    except Exception as e:
        QMessageBox.critical(None, "Erreur Critique", 
                           f"Erreur critique de l'application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
