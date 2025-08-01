"""
Login widget for user authentication
Replaces login.html template with native PyQt interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFrame,
                            QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette
import sys

class LoginWidget(QWidget):
    """Login widget for user authentication"""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(object)  # Emits the authenticated user
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DentisteDB - Connexion")
        self.setMinimumSize(500, 450)
        self.resize(600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Main layout with proper centering
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title_label = QLabel("DentisteDB")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2E7D32; margin-bottom: 20px;")
        
        # Subtitle
        subtitle_label = QLabel("Système de Gestion de Cabinet Dentaire")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 30px;")
        
        # Login form frame
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Username field
        username_label = QLabel("Nom d'utilisateur:")
        username_label.setStyleSheet("font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.returnPressed.connect(self.handle_login)
        
        # Password field
        password_label = QLabel("Mot de passe:")
        password_label.setStyleSheet("font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Login button
        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setMinimumHeight(40)
        
        # Add widgets to form layout
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        
        # Add everything to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(form_frame)
        
        # Add some spacing at the bottom
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Set focus to username field
        self.username_input.setFocus()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.show_error("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Disable button during login attempt
        self.login_button.setEnabled(False)
        self.login_button.setText("Connexion en cours...")
        
        # Attempt login
        success, message = self.auth_service.login(username, password)
        
        if success:
            # Emit signal with authenticated user
            user = self.auth_service.get_current_user()
            self.login_successful.emit(user)
        else:
            self.show_error("Erreur de connexion", message)
            # Clear password field
            self.password_input.clear()
            self.password_input.setFocus()
        
        # Re-enable button
        self.login_button.setEnabled(True)
        self.login_button.setText("Se connecter")
    
    def show_error(self, title, message):
        """Show error message dialog"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
            }
        """)
        msg_box.exec_()
    
    def clear_fields(self):
        """Clear input fields"""
        self.username_input.clear()
        self.password_input.clear()
        self.username_input.setFocus()
    
    def center_on_screen(self):
        """Center the widget on screen"""
        screen = QApplication.desktop().screenGeometry()
        widget = self.geometry()
        x = (screen.width() - widget.width()) // 2
        y = (screen.height() - widget.height()) // 2
        self.move(x, y)
    
    def showEvent(self, event):
        """Override showEvent to ensure proper centering when widget is shown"""
        super().showEvent(event)
        # Ensure the widget is properly sized and visible
        self.adjustSize()
        self.raise_()
        self.activateWindow()
