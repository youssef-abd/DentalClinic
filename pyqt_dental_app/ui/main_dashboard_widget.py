"""
Main Dashboard Widget
Container for all dashboard views with tabbed interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QPushButton, QLabel, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

try:
    from .financial_dashboard_widget import FinancialDashboardWidget
    from .patient_dashboard_widget import PatientDashboardWidget
    from ..services.dashboard_service_real import RealDashboardService
    REAL_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Real service not available, falling back to simple service: {e}")
    try:
        from ..services.dashboard_service_simple import DashboardService
        REAL_SERVICE_AVAILABLE = False
    except ImportError as e2:
        print(f"Import error in main_dashboard_widget: {e2}")
        REAL_SERVICE_AVAILABLE = False

class MainDashboardWidget(QWidget):
    """Main dashboard container with multiple dashboard views"""
    
    def __init__(self, parent=None, session=None, patient_service=None, visit_service=None, expense_service=None):
        super().__init__(parent)
        
        # Store services
        self.patient_service = patient_service
        self.visit_service = visit_service
        self.expense_service = expense_service
        
        # Initialize dashboard service with real data
        if REAL_SERVICE_AVAILABLE:
            self.dashboard_service = RealDashboardService(session)
            print("✅ Using real database service for dashboards")
        else:
            from ..services.dashboard_service_simple import DashboardService
            self.dashboard_service = DashboardService()
            print("⚠️ Using mock data service for dashboards")
        
        # Setup UI
        self.init_ui()
        
        # Setup auto-refresh timer (10 minutes)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all_dashboards)
        self.refresh_timer.start(600000)  # 10 minutes in milliseconds
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create header
        self.create_header(layout)
        
        # Create tabbed interface
        self.create_dashboard_tabs(layout)
    
    def create_header(self, layout):
        """Create main dashboard header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:0.5 #34495e, stop:1 #2c3e50);
                border-bottom: 3px solid #3498db;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        # Title section
        title_layout = QVBoxLayout()
        
        main_title = QLabel("📊 Tableaux de Bord")
        main_title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white;
            margin: 0px;
        """)
        title_layout.addWidget(main_title)
        
        subtitle = QLabel("Vue d'ensemble de votre cabinet dentaire")
        subtitle.setStyleSheet("""
            font-size: 14px; 
            color: #bdc3c7;
            margin: 0px;
        """)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Action buttons
        self.create_header_buttons(header_layout)
        
        layout.addWidget(header_frame)
    
    def create_header_buttons(self, layout):
        """Create header action buttons"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all_dashboards)
        buttons_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("📊 Exporter")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        export_btn.clicked.connect(self.export_dashboard_data)
        buttons_layout.addWidget(export_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Paramètres")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        settings_btn.clicked.connect(self.open_dashboard_settings)
        buttons_layout.addWidget(settings_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_dashboard_tabs(self, layout):
        """Create tabbed dashboard interface"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #ecf0f1;
            }
            
            QTabBar::tab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 12px 25px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #95a5a6;
                color: white;
            }
            
            QTabBar::tab:selected {
                border-bottom: 3px solid #2980b9;
            }
        """)
        
        # Create dashboard instances
        try:
            # Financial Dashboard
            self.financial_dashboard = FinancialDashboardWidget(
                dashboard_service=self.dashboard_service
            )
            self.tab_widget.addTab(self.financial_dashboard, "💰 Financier")
            
            # Patient Dashboard
            self.patient_dashboard = PatientDashboardWidget(
                dashboard_service=self.dashboard_service
            )
            self.tab_widget.addTab(self.patient_dashboard, "👥 Patients")
            
            # Store references for easy access
            self.dashboards = [
                self.financial_dashboard,
                self.patient_dashboard
            ]
            
        except Exception as e:
            print(f"Error creating dashboards: {e}")
            # Create error tab
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"Erreur lors du chargement des tableaux de bord:\n{str(e)}")
            error_label.setStyleSheet("color: red; font-size: 16px; padding: 50px;")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            self.tab_widget.addTab(error_widget, "❌ Erreur")
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.tab_widget)
    

    
    def refresh_all_dashboards(self):
        """Refresh all dashboard data"""
        try:
            print("Refreshing all dashboards...")
            
            # Refresh each dashboard
            for dashboard in getattr(self, 'dashboards', []):
                if hasattr(dashboard, 'load_data'):
                    try:
                        dashboard.load_data()
                    except Exception as e:
                        print(f"Error refreshing dashboard {type(dashboard).__name__}: {e}")
            
            print("Dashboard refresh completed")
            
        except Exception as e:
            print(f"Error during dashboard refresh: {e}")
    
    def on_tab_changed(self, index):
        """Handle tab change event"""
        try:
            current_widget = self.tab_widget.widget(index)
            if current_widget and hasattr(current_widget, 'load_data'):
                # Refresh data when switching to a tab
                current_widget.load_data()
        except Exception as e:
            print(f"Error handling tab change: {e}")
    
    def export_dashboard_data(self):
        """Export dashboard data to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            from datetime import datetime
            import json
            
            # Get export file path
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exporter les données du tableau de bord",
                f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                # Collect data from dashboard service
                dashboard_data = {
                    'export_date': datetime.now().isoformat(),
                    'summary': self.dashboard_service.get_dashboard_summary(),
                    'kpis': self.dashboard_service.get_kpi_summary()
                }
                
                # Save to file
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(dashboard_data, f, indent=2, ensure_ascii=False, default=str)
                
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Les données ont été exportées vers:\n{filename}"
                )
                
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"Erreur lors de l'export des données:\n{str(e)}"
            )
    
    def open_dashboard_settings(self):
        """Open dashboard settings dialog"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QSpinBox, QFormLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Paramètres du Tableau de Bord")
            dialog.setFixedSize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Settings form
            form_layout = QFormLayout()
            
            # Auto-refresh interval
            refresh_spinbox = QSpinBox()
            refresh_spinbox.setRange(1, 60)
            refresh_spinbox.setValue(10)  # Default 10 minutes
            refresh_spinbox.setSuffix(" minutes")
            form_layout.addRow("Actualisation automatique:", refresh_spinbox)
            
            # Enable/disable specific dashboards
            main_checkbox = QCheckBox()
            main_checkbox.setChecked(True)
            form_layout.addRow("Tableau principal:", main_checkbox)
            
            financial_checkbox = QCheckBox()
            financial_checkbox.setChecked(True)
            form_layout.addRow("Tableau financier:", financial_checkbox)
            
            patient_checkbox = QCheckBox()
            patient_checkbox.setChecked(True)
            form_layout.addRow("Tableau patients:", patient_checkbox)
            
            layout.addLayout(form_layout)
            
            # Buttons
            buttons_layout = QHBoxLayout()
            
            save_btn = QPushButton("Enregistrer")
            save_btn.clicked.connect(lambda: self.save_dashboard_settings(
                refresh_spinbox.value(),
                main_checkbox.isChecked(),
                financial_checkbox.isChecked(),
                patient_checkbox.isChecked(),
                dialog
            ))
            buttons_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("Annuler")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)
            
            layout.addLayout(buttons_layout)
            
            dialog.exec_()
            
        except Exception as e:
            print(f"Error opening dashboard settings: {e}")
    
    def save_dashboard_settings(self, refresh_interval, main_enabled, financial_enabled, patient_enabled, dialog):
        """Save dashboard settings"""
        try:
            # Update refresh timer
            self.refresh_timer.stop()
            self.refresh_timer.start(refresh_interval * 60000)  # Convert to milliseconds
            
            # Enable/disable tabs (simplified implementation)
            # In a full implementation, you might want to hide/show tabs
            
            dialog.accept()
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Paramètres sauvegardés",
                "Les paramètres du tableau de bord ont été mis à jour."
            )
            
        except Exception as e:
            print(f"Error saving dashboard settings: {e}")
    
    def get_current_dashboard(self):
        """Get currently active dashboard"""
        return self.tab_widget.currentWidget()
    
    def switch_to_dashboard(self, dashboard_name):
        """Switch to specific dashboard by name"""
        dashboard_map = {
            
            'financial': 0,
            'patient': 1
        }
        
        if dashboard_name in dashboard_map:
            self.tab_widget.setCurrentIndex(dashboard_map[dashboard_name])
    
    def add_custom_dashboard(self, widget, title):
        """Add a custom dashboard tab"""
        try:
            self.tab_widget.addTab(widget, title)
            if hasattr(self, 'dashboards'):
                self.dashboards.append(widget)
        except Exception as e:
            print(f"Error adding custom dashboard: {e}")
    
    def closeEvent(self, event):
        """Handle widget close event"""
        try:
            # Stop refresh timer
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
            
            # Close dashboard service
            if hasattr(self, 'dashboard_service'):
                del self.dashboard_service
                
            event.accept()
        except Exception as e:
            print(f"Error during dashboard close: {e}")
            event.accept()
