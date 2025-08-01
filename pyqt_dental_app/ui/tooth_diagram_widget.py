"""
Interactive Tooth Diagram Widget for Dental Chart Management
Professional-grade dental chart with realistic tooth representations and interactive features
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QButtonGroup, QTextEdit, QMessageBox, QFrame, QScrollArea,
                            QGridLayout, QGroupBox, QSplitter, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPalette, 
                        QPolygon, QPainterPath, QLinearGradient)
import math

class ToothWidget(QWidget):
    """Individual tooth widget with realistic shape and interactive features"""
    
    tooth_clicked = pyqtSignal(int, str)  # tooth_number, current_status
    
    def __init__(self, tooth_number, status='normal', parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.status = status
        self.is_hovered = False
        self.is_selected = False
        
        # Tooth dimensions
        self.setFixedSize(50, 60)
        self.setToolTip(f"Dent #{tooth_number}")
        self.setCursor(Qt.PointingHandCursor)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def set_status(self, status):
        """Update tooth status and repaint"""
        self.status = status
        self.update()
    
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        self.update()
    
    def get_status_color(self):
        """Get color based on tooth status"""
        colors = {
            'normal': QColor(229, 231, 235),      # Light gray
            'carie': QColor(239, 68, 68),         # Red
            'couronne': QColor(59, 130, 246),     # Blue
            'bridge': QColor(139, 92, 246),       # Purple
            'implant': QColor(16, 185, 129),      # Green
            'extraction': QColor(107, 114, 128),  # Dark gray
            'traitement': QColor(245, 158, 11),   # Orange
            'observation': QColor(236, 72, 153)   # Pink
        }
        return colors.get(self.status, colors['normal'])
    
    def paintEvent(self, event):
        """Custom paint event for realistic tooth representation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get tooth color
        base_color = self.get_status_color()
        
        # Create gradient for 3D effect
        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.is_hovered:
            gradient.setColorAt(0, base_color.lighter(120))
            gradient.setColorAt(1, base_color.darker(110))
        else:
            gradient.setColorAt(0, base_color.lighter(110))
            gradient.setColorAt(1, base_color.darker(120))
        
        # Draw tooth shape based on position
        self.draw_tooth_shape(painter, gradient)
        
        # Draw selection highlight
        if self.is_selected:
            painter.setPen(QPen(QColor(59, 130, 246), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(2, 2, self.width()-4, self.height()-4, 8, 8)
        
        # Draw tooth number
        painter.setPen(QPen(Qt.black))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, str(self.tooth_number))
    
    def draw_tooth_shape(self, painter, gradient):
        """Draw realistic tooth shape based on tooth type"""
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        
        # Determine tooth type based on number
        tooth_type = self.get_tooth_type()
        
        if tooth_type == 'incisor':
            self.draw_incisor(painter)
        elif tooth_type == 'canine':
            self.draw_canine(painter)
        elif tooth_type == 'premolar':
            self.draw_premolar(painter)
        elif tooth_type == 'molar':
            self.draw_molar(painter)
    
    def get_tooth_type(self):
        """Determine tooth type based on tooth number using FDI numbering"""
        # FDI numbering system (11-18, 21-28, 31-38, 41-48)
        # Last digit indicates position in quadrant (1-8)
        pos = self.tooth_number % 10
        
        if pos in [1, 2]:  # Central and lateral incisors
            return 'incisor'
        elif pos == 3:     # Canine
            return 'canine'
        elif pos in [4, 5]: # Premolars
            return 'premolar'
        else:              # Molars
            return 'molar'
    
    def draw_incisor(self, painter):
        """Draw incisor tooth shape with variations for central and lateral"""
        path = QPainterPath()
        width, height = self.width(), self.height()
        
        # Get position in quadrant (1-8)
        pos = self.tooth_number % 10
        is_upper = self.tooth_number < 30  # Upper jaw if tooth number < 30
        
        if pos == 1:  # Central incisor
            path.moveTo(width*0.3, height*0.1)
            path.quadTo(width*0.5, 0, width*0.7, height*0.1)
            path.quadTo(width*0.8, height*0.4, width*0.8, height*0.7)
            path.quadTo(width*0.8, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.2, height*0.9, width*0.2, height*0.7)
            path.quadTo(width*0.2, height*0.4, width*0.3, height*0.1)
        else:  # Lateral incisor
            path.moveTo(width*0.35, height*0.15)
            path.quadTo(width*0.5, height*0.05, width*0.65, height*0.15)
            path.quadTo(width*0.75, height*0.4, width*0.75, height*0.8)
            path.quadTo(width*0.75, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.25, height*0.9, width*0.25, height*0.8)
            path.quadTo(width*0.25, height*0.4, width*0.35, height*0.15)
        
        painter.drawPath(path)

    def draw_canine(self, painter):
        """Draw canine tooth shape (pointed)"""
        path = QPainterPath()
        width, height = self.width(), self.height()
        
        path.moveTo(width*0.5, height*0.05)
        path.quadTo(width*0.7, height*0.1, width*0.7, height*0.3)
        path.quadTo(width*0.7, height*0.6, width*0.6, height*0.8)
        path.quadTo(width*0.5, height*0.9, width*0.4, height*0.8)
        path.quadTo(width*0.3, height*0.6, width*0.3, height*0.3)
        path.quadTo(width*0.3, height*0.1, width*0.5, height*0.05)
        
        # Add a slight curve to the tip for more realism
        path.moveTo(width*0.45, height*0.05)
        path.quadTo(width*0.5, height*0.02, width*0.55, height*0.05)
        
        painter.drawPath(path)

    def draw_premolar(self, painter):
        """Draw premolar tooth shape with variations for first and second premolars"""
        path = QPainterPath()
        width, height = self.width(), self.height()
        
        # Get position in quadrant (1-8)
        pos = self.tooth_number % 10
        
        if pos == 4:  # First premolar
            # Occlusal surface with two cusps
            path.moveTo(width*0.2, height*0.2)
            path.quadTo(width*0.3, height*0.1, width*0.5, height*0.1)
            path.quadTo(width*0.7, height*0.1, width*0.8, height*0.2)
            path.quadTo(width*0.8, height*0.4, width*0.8, height*0.7)
            path.quadTo(width*0.8, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.2, height*0.9, width*0.2, height*0.7)
            path.quadTo(width*0.2, height*0.4, width*0.2, height*0.2)
            
            # Add central groove
            path.moveTo(width*0.4, height*0.15)
            path.quadTo(width*0.5, height*0.2, width*0.6, height*0.15)
            
        else:  # Second premolar
            # More rounded occlusal surface with multiple cusps
            path.moveTo(width*0.15, height*0.25)
            path.quadTo(width*0.3, height*0.1, width*0.5, height*0.1)
            path.quadTo(width*0.7, height*0.1, width*0.85, height*0.25)
            path.quadTo(width*0.9, height*0.4, width*0.85, height*0.7)
            path.quadTo(width*0.8, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.2, height*0.9, width*0.15, height*0.7)
            path.quadTo(width*0.1, height*0.4, width*0.15, height*0.25)
            
            # Add central groove and fossa
            path.moveTo(width*0.35, height*0.2)
            path.quadTo(width*0.5, height*0.25, width*0.65, height*0.2)
            path.moveTo(width*0.4, height*0.3)
            path.quadTo(width*0.5, height*0.35, width*0.6, height*0.3)
        
        painter.drawPath(path)

    def draw_molar(self, painter):
        """Draw molar tooth shape with variations for different molars"""
        path = QPainterPath()
        width, height = self.width(), self.height()
        
        # Get position in quadrant (1-8)
        pos = self.tooth_number % 10
        
        if pos == 6:  # First molar (largest)
            # Occlusal surface with multiple cusps
            path.moveTo(width*0.1, height*0.2)
            path.quadTo(width*0.2, height*0.1, width*0.4, height*0.1)
            path.quadTo(width*0.5, height*0.05, width*0.6, height*0.1)
            path.quadTo(width*0.8, height*0.1, width*0.9, height*0.2)
            path.quadTo(width*0.95, height*0.4, width*0.9, height*0.7)
            path.quadTo(width*0.85, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.15, height*0.9, width*0.1, height*0.7)
            path.quadTo(width*0.05, height*0.4, width*0.1, height*0.2)
            
            # Add central grooves
            path.moveTo(width*0.3, height*0.15)
            path.quadTo(width*0.5, height*0.2, width*0.7, height*0.15)
            path.moveTo(width*0.4, height*0.25)
            path.quadTo(width*0.5, height*0.3, width*0.6, height*0.25)
            
        elif pos == 7:  # Second molar
            path.moveTo(width*0.15, height*0.25)
            path.quadTo(width*0.3, height*0.15, width*0.5, height*0.1)
            path.quadTo(width*0.7, height*0.15, width*0.85, height*0.25)
            path.quadTo(width*0.95, height*0.4, width*0.9, height*0.75)
            path.quadTo(width*0.85, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.15, height*0.9, width*0.1, height*0.75)
            path.quadTo(width*0.05, height*0.4, width*0.15, height*0.25)
            
            # Add central groove
            path.moveTo(width*0.4, height*0.2)
            path.quadTo(width*0.5, height*0.25, width*0.6, height*0.2)
            
        else:  # Third molar (wisdom tooth) or other
            path.moveTo(width*0.2, height*0.3)
            path.quadTo(width*0.4, height*0.2, width*0.6, height*0.2)
            path.quadTo(width*0.8, height*0.3, width*0.8, height*0.7)
            path.quadTo(width*0.8, height*0.9, width*0.5, height*0.95)
            path.quadTo(width*0.2, height*0.9, width*0.2, height*0.7)
            path.quadTo(width*0.2, height*0.5, width*0.2, height*0.3)
        
        painter.drawPath(path)

    def enterEvent(self, event):
        """Mouse enter event"""
        self.is_hovered = True
        self.update()
    
    def leaveEvent(self, event):
        """Mouse leave event"""
        self.is_hovered = False
        self.update()
    
    def mousePressEvent(self, event):
        """Mouse click event"""
        if event.button() == Qt.LeftButton:
            self.tooth_clicked.emit(self.tooth_number, self.status)

class ToothDiagramWidget(QWidget):
    """Complete interactive tooth diagram widget"""
    
    tooth_status_changed = pyqtSignal(int, str)  # tooth_number, new_status
    
    def __init__(self, tooth_service, patient_id=None, parent=None):
        super().__init__(parent)
        self.tooth_service = tooth_service
        self.patient_id = patient_id
        self.selected_tooth = None
        self.selected_status = 'normal'
        self.tooth_widgets = {}
        
        self.init_ui()
        if patient_id:
            self.load_patient_chart(patient_id)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Diagramme Dentaire Interactif")
        self.setMinimumSize(1000, 600)  # Increased height to 600 for better control panel space
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(5)  # Reduced spacing for more compact layout
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Dental Chart
        chart_panel = self.create_chart_panel()
        splitter.addWidget(chart_panel)
        
        # Right panel - Controls and Info
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # Set splitter proportions - more space for chart, less for sidebar
        splitter.setSizes([800, 200])
        main_layout.addWidget(splitter)
    
    def create_chart_panel(self):
        """Create the dental chart panel with FDI numbering system"""
        chart_frame = QFrame()
        # Set size constraints to prevent stretching
        chart_frame.setMaximumHeight(200)  # Limit height to keep teeth close
        chart_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                padding: 0px;
            }
        """)
        
        chart_layout = QGridLayout(chart_frame)
        chart_layout.setSpacing(10)  # Moderate spacing for consistent appearance
        chart_layout.setContentsMargins(10, 10, 10, 10)  # Small margins for better appearance
        chart_layout.setVerticalSpacing(15)  # Consistent vertical spacing between upper and lower teeth
        
        # Debug: Print layout settings
        print(f"DEBUG: Chart layout spacing: {chart_layout.spacing()}")
        print(f"DEBUG: Chart layout vertical spacing: {chart_layout.verticalSpacing()}")
        margins = chart_frame.contentsMargins()
        print(f"DEBUG: Chart layout margins: left={margins.left()}, top={margins.top()}, right={margins.right()}, bottom={margins.bottom()}")
        
        # Upper jaw - continuous row without separations
        upper_widget = QWidget()
        upper_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        upper_widget.setContentsMargins(0, 0, 0, 0)
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setSpacing(1)  # Teeth almost touching each other
        upper_layout.setContentsMargins(0, 0, 0, 0)  # No margins around teeth
        
        # Create teeth 18-11 (right to left) - Upper Right
        self.tooth_widgets = {}
        for tooth_num in range(18, 10, -1):
            tooth = ToothWidget(tooth_num)
            tooth.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_widgets[tooth_num] = tooth
            upper_layout.addWidget(tooth)
        
        # Create teeth 21-28 (left to right) - Upper Left
        for tooth_num in range(21, 29):
            tooth = ToothWidget(tooth_num)
            tooth.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_widgets[tooth_num] = tooth
            upper_layout.addWidget(tooth)
        
        chart_layout.addWidget(upper_widget, 0, 0)  # Row 0, Column 0
        # Force upper widget to specific position
        upper_widget.setFixedHeight(60)  # Match tooth height
        
        # Lower jaw - continuous row without separations
        lower_widget = QWidget()
        lower_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        lower_widget.setContentsMargins(0, 0, 0, 0)  # Normal margins
        lower_layout = QHBoxLayout(lower_widget)
        lower_layout.setSpacing(1)  # Teeth almost touching each other
        lower_layout.setContentsMargins(0, 0, 0, 0)  # No margins around teeth
        
        # Create teeth 48-41 (right to left) - Lower Right
        for tooth_num in range(48, 40, -1):
            tooth = ToothWidget(tooth_num)
            tooth.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_widgets[tooth_num] = tooth
            lower_layout.addWidget(tooth)
        
        # Create teeth 31-38 (left to right) - Lower Left
        for tooth_num in range(31, 39):
            tooth = ToothWidget(tooth_num)
            tooth.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_widgets[tooth_num] = tooth
            lower_layout.addWidget(tooth)
        
        chart_layout.addWidget(lower_widget, 1, 0)  # Row 1, Column 0 (directly below upper)
        # Force lower widget to specific position
        lower_widget.setFixedHeight(60)  # Match tooth height
        
        # Remove absolute positioning to prevent spacing changes on tab switches
        
        # Force immediate layout updates
        chart_layout.update()
        chart_frame.updateGeometry()
        upper_widget.updateGeometry()
        lower_widget.updateGeometry()
        
        # Debug: Print widget information
        print(f"DEBUG: Upper widget height: {upper_widget.height()}, size hint: {upper_widget.sizeHint()}")
        print(f"DEBUG: Lower widget height: {lower_widget.height()}, size hint: {lower_widget.sizeHint()}")
        lower_margins = lower_widget.contentsMargins()
        print(f"DEBUG: Lower widget margins: left={lower_margins.left()}, top={lower_margins.top()}, right={lower_margins.right()}, bottom={lower_margins.bottom()}")
        
        return chart_frame
    
    def create_control_panel(self):
        """Create the control panel"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Status selection
        status_group = QGroupBox("Sélectionner l'État")
        status_group.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(10)  # Add spacing between status buttons
        
        self.status_buttons = QButtonGroup()
        statuses = self.tooth_service.get_available_statuses()
        
        for i, status_info in enumerate(statuses):
            btn = QPushButton(status_info['name'])
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {status_info['color']};
                    color: {'white' if status_info['key'] in ['carie', 'bridge', 'extraction'] else 'black'};
                    border: 2px solid #D1D5DB;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                    margin: 8px;
                    min-height: 15px;
                }}
                QPushButton:checked {{
                    border-color: #3B82F6;
                    border-width: 3px;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            
            if status_info['key'] == 'normal':
                btn.setChecked(True)
            
            btn.clicked.connect(lambda checked, key=status_info['key']: self.set_selected_status(key))
            self.status_buttons.addButton(btn, i)
            status_layout.addWidget(btn)
        
        layout.addWidget(status_group)
        
        # Tooth information
        info_group = QGroupBox("Information sur la Dent")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout(info_group)
        
        self.tooth_info_label = QLabel("Tooth diagram widget for interactive dental chart with FDI numbering")
        self.tooth_info_label.setWordWrap(True)
        self.tooth_info_label.setStyleSheet("padding: 10px; background-color: white; border-radius: 5px;")
        info_layout.addWidget(self.tooth_info_label)
        
        # Notes section
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notes sur la dent sélectionnée...")
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setStyleSheet("border: 1px solid #D1D5DB; border-radius: 5px; padding: 5px;")
        info_layout.addWidget(self.notes_edit)
        
        layout.addWidget(info_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Sauvegarder")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.save_btn.clicked.connect(self.save_tooth_status)
        
        self.reset_btn = QPushButton("Réinitialiser")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_selected_tooth)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return panel
    
    def create_legend(self):
        """Create color legend for tooth statuses"""
        legend_frame = QFrame()
        legend_frame.setStyleSheet("background-color: #F3F4F6; border-radius: 8px; padding: 10px;")
        
        layout = QVBoxLayout(legend_frame)
        
        title = QLabel("Légende")
        title.setFont(QFont("Arial", 10, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create legend items in a grid
        grid_layout = QGridLayout()
        statuses = self.tooth_service.get_available_statuses()
        
        for i, status_info in enumerate(statuses):
            # Color box
            color_box = QLabel()
            color_box.setFixedSize(15, 15)
            color_box.setStyleSheet(f"background-color: {status_info['color']}; border: 1px solid #999;")
            
            # Label
            label = QLabel(status_info['name'])
            label.setFont(QFont("Arial", 8))
            
            row = i // 2
            col = (i % 2) * 2
            grid_layout.addWidget(color_box, row, col)
            grid_layout.addWidget(label, row, col + 1)
        
        layout.addLayout(grid_layout)
        return legend_frame
    
    def load_patient_chart(self, patient_id):
        """Load tooth chart for a specific patient"""
        self.patient_id = patient_id
        tooth_chart = self.tooth_service.get_patient_tooth_chart(patient_id)
        
        for tooth_number, status in tooth_chart.items():
            if tooth_number in self.tooth_widgets:
                self.tooth_widgets[tooth_number].set_status(status)
        
        self.update_summary()
    
    def on_tooth_clicked(self, tooth_number, current_status):
        """Handle tooth click event"""
        # Clear previous selection
        if self.selected_tooth:
            self.tooth_widgets[self.selected_tooth].set_selected(False)
        
        # Set new selection
        self.selected_tooth = tooth_number
        self.tooth_widgets[tooth_number].set_selected(True)
        
        # Update tooth info
        self.update_tooth_info(tooth_number)
        
        # Apply selected status to clicked tooth
        if self.selected_status != current_status:
            self.tooth_widgets[tooth_number].set_status(self.selected_status)
            
            # Save to database
            if self.patient_id:
                notes = self.notes_edit.toPlainText()
                success = self.tooth_service.update_tooth_status(
                    self.patient_id, tooth_number, self.selected_status, notes
                )
                if success:
                    self.tooth_status_changed.emit(tooth_number, self.selected_status)
                    self.update_summary()
    
    def update_tooth_info(self, tooth_number):
        """Update tooth information display"""
        if not self.patient_id:
            return
        
        details = self.tooth_service.get_tooth_details(self.patient_id, tooth_number)
        tooth_type = self.get_tooth_name(tooth_number)
        
        info_text = f"""
        <b>Dent #{tooth_number}</b> - {tooth_type}<br>
        <b>État:</b> {self.get_status_name(details['status'])}<br>
        <b>Date d'enregistrement:</b> {details['date_recorded'] or 'Non enregistrée'}
        """
        
        self.tooth_info_label.setText(info_text)
        self.notes_edit.setPlainText(details['notes'] or '')
    
    def get_tooth_name(self, tooth_number):
        """Get descriptive name for tooth"""
        # Convert to position in quadrant
        quadrant = ((tooth_number - 1) // 8) + 1
        pos = ((tooth_number - 1) % 8) + 1
        
        quadrant_names = {1: "Supérieur Droit", 2: "Supérieur Gauche", 
                         3: "Inférieur Gauche", 4: "Inférieur Droit"}
        
        tooth_names = {1: "Incisive Centrale", 2: "Incisive Latérale", 3: "Canine",
                      4: "1ère Prémolaire", 5: "2ème Prémolaire", 
                      6: "1ère Molaire", 7: "2ème Molaire", 8: "3ème Molaire"}
        
        return f"{tooth_names.get(pos, 'Dent')} {quadrant_names.get(quadrant, '')}"
    
    def get_status_name(self, status):
        """Get display name for status"""
        status_names = {
            'normal': 'Normal',
            'carie': 'Carie',
            'couronne': 'Couronne',
            'bridge': 'Bridge',
            'implant': 'Implant',
            'extraction': 'Extraction',
            'traitement': 'En Traitement',
            'observation': 'À Observer'
        }
        return status_names.get(status, status.title())
    
    def set_selected_status(self, status):
        """Set the currently selected status"""
        self.selected_status = status
    
    def save_tooth_status(self):
        """Save current tooth status"""
        if not self.selected_tooth or not self.patient_id:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une dent.")
            return
        
        notes = self.notes_edit.toPlainText()
        success = self.tooth_service.update_tooth_status(
            self.patient_id, self.selected_tooth, self.selected_status, notes
        )
        
        if success:
            QMessageBox.information(self, "Succès", "État de la dent sauvegardé avec succès.")
            self.update_summary()
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la sauvegarde.")
    
    def reset_selected_tooth(self):
        """Reset selected tooth to normal"""
        if not self.selected_tooth:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une dent.")
            return
        
        self.tooth_widgets[self.selected_tooth].set_status('normal')
        if self.patient_id:
            self.tooth_service.update_tooth_status(self.patient_id, self.selected_tooth, 'normal')
            self.update_summary()
    
    def update_summary(self):
        """Update dental summary - removed to save space"""
        # Summary section removed to gain space in the control panel
        pass
