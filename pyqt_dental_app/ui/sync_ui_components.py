# sync_ui_components.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
import json

from ..sync_service import sync_service, SyncStatus, SyncResult

class SyncStatusWidget(QWidget):
    """Widget to display sync status in your main window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        try:
            # Connect to sync service
            sync_service.add_status_callback(self.on_sync_status_changed)
            
            # Update UI with current status
            self.update_status_display()
        except Exception as e:
            print(f"Error initializing SyncStatusWidget: {e}")
            self.status_label.setText("Sync: Error initializing")
            self.status_icon.setText("❌")
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        layout.addWidget(self.status_icon)
        
        # Status text
        self.status_label = QLabel("Sync: Not started")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Manual sync button
        self.sync_button = QPushButton("Sync Now")
        self.sync_button.clicked.connect(self.manual_sync)
        layout.addWidget(self.sync_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙")
        self.settings_button.setMaximumWidth(30)
        self.settings_button.clicked.connect(self.show_sync_settings)
        layout.addWidget(self.settings_button)
        
        self.setLayout(layout)
    
    def on_sync_status_changed(self, result: SyncResult):
        """Called when sync status changes"""
        # Use QTimer to ensure UI updates happen on main thread
        QTimer.singleShot(0, lambda: self.update_status_display(result))
    
    def update_status_display(self, result: SyncResult = None):
        """Update the status display"""
        if not result:
            status = sync_service.get_sync_status()
            if status['last_result']:
                # Recreate SyncResult from dict
                result = SyncResult(
                    status=SyncStatus(status['last_result']['status']),
                    message=status['last_result']['message'],
                    timestamp=datetime.fromisoformat(status['last_result']['timestamp']),
                    patients_synced=status['last_result']['patients_synced'],
                    visits_synced=status['last_result']['visits_synced'],
                    error=status['last_result']['error']
                )
        
        if not result:
            self.status_label.setText("Sync: Not started")
            self.status_icon.setText("⚪")
            return
        
        # Update icon based on status
        if result.status == SyncStatus.IDLE:
            self.status_icon.setText("⚪")
            self.status_label.setText("Sync: Idle")
        elif result.status == SyncStatus.SCHEDULED:
            self.status_icon.setText("🕒")
            self.status_label.setText("Sync: Scheduled")
        elif result.status == SyncStatus.SYNCING:
            self.status_icon.setText("🔄")
            self.status_label.setText("Sync: In progress...")
            self.sync_button.setEnabled(False)
        elif result.status == SyncStatus.SUCCESS:
            self.status_icon.setText("✅")
            time_str = result.timestamp.strftime("%H:%M")
            total_synced = result.patients_synced + result.visits_synced
            self.status_label.setText(f"Sync: Success ({total_synced} records) at {time_str}")
            self.sync_button.setEnabled(True)
        elif result.status == SyncStatus.ERROR:
            self.status_icon.setText("❌")
            self.status_label.setText(f"Sync: Error - {result.message}")
            self.sync_button.setEnabled(True)
    
    def manual_sync(self):
        """Trigger manual sync"""
        try:
            self.sync_button.setEnabled(False)
            # Run sync in separate thread to avoid blocking UI
            QTimer.singleShot(100, lambda: sync_service.sync_now())
        except Exception as e:
            print(f"Error in manual_sync: {e}")
            self.sync_button.setEnabled(True)
            self.status_label.setText("Sync: Error triggering")
            self.status_icon.setText("❌")
    
    def show_sync_settings(self):
        """Show sync settings dialog"""
        try:
            dialog = SyncSettingsDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Error showing sync settings: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not open sync settings: {str(e)}")

class SyncSettingsDialog(QDialog):
    """Dialog for sync settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sync Settings")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Auto sync checkbox
        self.auto_sync_check = QCheckBox("Enable automatic sync")
        layout.addWidget(self.auto_sync_check)
        
        # Sync interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Sync interval:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 1440)  # 5 minutes to 24 hours
        self.interval_spin.setSuffix(" minutes")
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)
        
        layout.addStretch()
        
        # Sync history
        layout.addWidget(QLabel("Recent sync history:"))
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(100)
        layout.addWidget(self.history_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_sync_btn = QPushButton("Test Sync")
        self.test_sync_btn.clicked.connect(self.test_sync)
        button_layout.addWidget(self.test_sync_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_current_settings(self):
        """Load current sync settings"""
        try:
            status = sync_service.get_sync_status()
            if status:
                self.auto_sync_check.setChecked(status.get('auto_sync_enabled', True))
                self.interval_spin.setValue(status.get('sync_interval_minutes', 30))
                
                # Load sync history (you might want to implement this)
                if status.get('last_result'):
                    last_result = status['last_result']
                    self.history_text.append(
                        f"{last_result['timestamp']}: {last_result['status']} - {last_result['message']}"
                    )
        except Exception as e:
            print(f"Error loading sync settings: {e}")
            # Set default values
            self.auto_sync_check.setChecked(True)
            self.interval_spin.setValue(30)
    
    def test_sync(self):
        """Test sync connection"""
        try:
            self.test_sync_btn.setEnabled(False)
            self.test_sync_btn.setText("Testing...")
            
            # Trigger sync and wait for result
            result = sync_service.sync_now()
            
            QTimer.singleShot(100, self.reset_test_button)
        except Exception as e:
            print(f"Error in test_sync: {e}")
            QTimer.singleShot(100, self.reset_test_button)
    
    def reset_test_button(self):
        self.test_sync_btn.setEnabled(True)
        self.test_sync_btn.setText("Test Sync")
    
    def save_settings(self):
        """Save sync settings"""
        try:
            sync_service.set_auto_sync(self.auto_sync_check.isChecked())
            sync_service.set_sync_interval(self.interval_spin.value())
            self.accept()
        except Exception as e:
            print(f"Error saving sync settings: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not save sync settings: {str(e)}")


# main_window_integration.py
class MainWindow(QMainWindow):  # Your existing main window class
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Start sync service when app starts
        self.start_sync_service()
        
        # Add sync status to status bar or toolbar
        self.add_sync_status_widget()
    
    def setup_ui(self):
        # Your existing UI setup
        pass
    
    def add_sync_status_widget(self):
        """Add sync status widget to the UI"""
        # Option 1: Add to status bar
        self.sync_status_widget = SyncStatusWidget()
        self.statusBar().addPermanentWidget(self.sync_status_widget)
        
        # Option 2: Add to toolbar
        # sync_toolbar = self.addToolBar("Sync")
        # sync_toolbar.addWidget(SyncStatusWidget())
    
    def start_sync_service(self):
        """Start the background sync service"""
        from sync_service import start_sync_service
        start_sync_service()
        
        # Show a brief status message
        self.statusBar().showMessage("Background sync started", 3000)
    
    def closeEvent(self, event):
        """Handle app closing"""
        from sync_service import stop_sync_service
        stop_sync_service()
        
        # Call parent close event
        super().closeEvent(event)


# app_startup.py - How to modify your main application startup
def main():
    app = QApplication(sys.argv)
    
    # Create main window (sync service starts automatically)
    window = MainWindow()
    window.show()
    
    # No need to run sync on startup anymore!
    # The background service will handle it
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()