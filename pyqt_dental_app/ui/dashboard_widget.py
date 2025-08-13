"""
Dashboard Widget
Main dashboard interface for dental practice management
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QScrollArea, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QProgressBar, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class DashboardWidget(QWidget):
    """Main dashboard interface"""
    
    def __init__(self, dashboard_service=None, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        
        self.init_ui()
        self.load_data()
        
        # Auto-refresh timer (every 5 minutes)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(300000)  # 5 minutes
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main widget inside scroll area
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)  # Increased margins
        layout.setSpacing(30)  # Increased spacing between sections
        
        # Header
        self.create_header(layout)
        
        # Key metrics cards
        self.create_metrics_section(layout)
        
        # Charts section
        self.create_charts_section(layout)
        
        # Tables section (only other tables, stock alerts moved)
        self.create_tables_section(layout)
        
        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_header(self, layout):
        """Create dashboard header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)  # Increased margins
        header_layout.setSpacing(20)  # Add spacing
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)  # Add spacing between title and subtitle
        
        title = QLabel("Tableau de Bord")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white; margin-bottom: 5px;")
        title_layout.addWidget(title)
        
        subtitle = QLabel(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        subtitle.setStyleSheet("font-size: 16px; color: #ecf0f1; margin-top: 5px;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setFixedHeight(45)  # Set fixed height
        refresh_btn.setMinimumWidth(120)  # Set minimum width
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                padding: 14px 27px;  
                margin: -2px -2px;   
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_frame)
    
    def create_metrics_section(self, layout):
        """Create key metrics cards matching financial dashboard style"""
        # Create a container frame with a light background
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        # Create a horizontal layout for the metrics
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(5, 5, 5, 5)
        metrics_layout.setSpacing(10)
        
        # Metrics data (will be updated with real data)
        self.metrics = {
            'patients_total': {'title': 'Total Patients', 'value': '0', 'description': 'Patients enregistrés', 'color': '#3498db', 'icon': '👥'},
            'patients_month': {'title': 'Nouveaux', 'value': '0', 'description': 'Nouveaux patients', 'color': '#2ecc71', 'icon': '👤'},
            'revenue_month': {'title': 'Revenus', 'value': '0 MAD', 'description': 'Chiffre d\'affaires', 'color': '#f39c12', 'icon': '💰'},
            'expenses_month': {'title': 'Dépenses', 'value': '0 MAD', 'description': 'Frais et charges', 'color': '#9b59b6', 'icon': '💸'},
            'unpaid_balance': {'title': 'Impayés', 'value': '0 MAD', 'description': 'Montants en attente', 'color': '#e67e22', 'icon': '⚠️'}
        }
        
        # Create metric cards
        for key, metric in self.metrics.items():
            card = self.create_kpi_card(
                metric['title'], 
                metric['value'], 
                metric['description'], 
                metric['icon'], 
                metric['color']
            )
            
            # Store reference for updates
            setattr(self, f'{key}_card', card)
            metrics_layout.addWidget(card)
        
        # Add the metrics frame to the main layout
        layout.addWidget(metrics_frame)
    
    def create_kpi_card(self, title, value, description, icon_name, color):
        """Create a professional KPI card matching financial dashboard style"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                min-width: 200px;
            }}
            QLabel#title {{
                color: #7f8c8d;
                font-size: 14px;
                font-weight: 500;
            }}
            QLabel#value {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
                margin: 5px 0;
            }}
            QLabel#description {{
                color: #7f8c8d;
                font-size: 12px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with icon and title
        header = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setObjectName("title")
        
        if icon_name:
            # Icon (using text as emoji for now)
            icon_label = QLabel(icon_name)
            icon_label.setStyleSheet("font-size: 20px;")
            header.addWidget(icon_label)
        
        header.addWidget(title_label)
        header.addStretch()
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setProperty("metric_value", True)  # For finding in load_data
        
        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("description")
        
        layout.addLayout(header)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        return card
    
    def create_charts_section(self, layout):
        """Create charts section"""
        charts_frame = QFrame()
        charts_frame.setMinimumHeight(400)  # Set minimum height for charts
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                margin: 10px;
            }
        """)
        
        charts_layout = QVBoxLayout(charts_frame)
        charts_layout.setSpacing(20)  # Add spacing
        
        # Section title
        title = QLabel("Analyses Graphiques")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px; padding: 10px;")
        charts_layout.addWidget(title)
        
        # Charts container
        charts_container = QHBoxLayout()
        charts_container.setSpacing(20)  # Add spacing between charts
        
        # Revenue chart
        self.revenue_chart = self.create_revenue_chart()
        self.revenue_chart.setMinimumSize(400, 300)  # Set minimum size
        charts_container.addWidget(self.revenue_chart)
        
        # Expenses chart
        self.expenses_chart = self.create_expenses_chart()
        self.expenses_chart.setMinimumSize(400, 300)  # Set minimum size
        charts_container.addWidget(self.expenses_chart)
        
        charts_layout.addLayout(charts_container)
        layout.addWidget(charts_frame)
    
    def create_revenue_chart(self):
        """Create revenue chart"""
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.set_title('Revenus des 6 derniers mois', fontsize=14, fontweight='bold')
        
        # Sample data (will be replaced with real data)
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        revenues = [12500, 18750, 9800, 15400, 21000, 18900]
        
        bars = ax.bar(months, revenues, color='#3498db', alpha=0.8)
        ax.set_ylabel('Revenus (MAD)')
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, revenues):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 200,
                   f'{value:,.0f}', ha='center', va='bottom', fontsize=10)
        
        fig.tight_layout()
        return canvas
    
    def create_expenses_chart(self):
        """Create expenses pie chart"""
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.set_title('Répartition des Dépenses', fontsize=14, fontweight='bold')
        
        # Sample data (will be replaced with real data)
        categories = ['Matériel', 'Salaires', 'Loyer', 'Utilities', 'Autres']
        amounts = [35, 30, 20, 10, 5]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
        
        wedges, texts, autotexts = ax.pie(amounts, labels=categories, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        # Improve text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        fig.tight_layout()
        return canvas
    
    def create_tables_section(self, layout):
        """Create tables section"""
        # Only create appointments table
        appointments_frame = self.create_appointments_table()
        
        # Create a container to center the appointments frame
        container = QHBoxLayout()
        container.addStretch()
        container.addWidget(appointments_frame)
        container.addStretch()
        
        layout.addLayout(container)
    
    def create_appointments_table(self):
        """Create recent appointments table"""
        frame = QFrame()
        frame.setMinimumHeight(300)  # Set minimum height
        frame.setMinimumWidth(400)   # Set minimum width
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title = QLabel("Prochains Rendez-vous")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; padding: 5px;")
        layout.addWidget(title)
        
        # Table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(3)
        self.appointments_table.setHorizontalHeaderLabels(['Heure', 'Patient', 'Traitement'])
        
        # Style the table
        self.appointments_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                alternate-background-color: #ffffff;
                selection-background-color: #3498db;
                gridline-color: #dee2e6;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #495057;
            }
        """)
        
        self.appointments_table.setAlternatingRowColors(True)
        self.appointments_table.horizontalHeader().setStretchLastSection(True)
        self.appointments_table.setMinimumHeight(220)  # Increased height
        self.appointments_table.verticalHeader().setDefaultSectionSize(35)  # Row height
        
        layout.addWidget(self.appointments_table)
        
        return frame
    
    def create_stock_alerts_table(self):
        """Create stock alerts table"""
        frame = QFrame()
        frame.setMinimumHeight(300)  # Set minimum height
        frame.setMinimumWidth(600)   # Increased minimum width for better visibility
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title = QLabel("Alertes Stock")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px; padding: 5px;")
        layout.addWidget(title)
        
        # Table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels(['Article', 'Stock', 'Status'])
        
        # Style the table
        self.stock_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
                alternate-background-color: #ffffff;
                selection-background-color: #e74c3c;
                gridline-color: #dee2e6;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #495057;
            }
        """)
        
        self.stock_table.setAlternatingRowColors(True)
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setMinimumHeight(220)  # Increased height
        self.stock_table.verticalHeader().setDefaultSectionSize(35)  # Row height
        
        layout.addWidget(self.stock_table)
        
        return frame
    
    def load_data(self):
        """Load dashboard data from real database"""
        if hasattr(self, 'dashboard_service') and self.dashboard_service:
            try:
                # Get real data from service
                data = self.dashboard_service.get_overview_data()
                if data:
                    print(f"Dashboard data loaded: {len(data)} metrics")
                    
                    # Update metrics with real data
                    self.update_metrics(data)
                    
                    # Update charts with real data
                    self.update_charts(data)
                    
                    # Update tables with real data
                    self.update_tables(data)
                    
                    print("✅ Dashboard updated with real data")
                else:
                    print("⚠️ No data returned from dashboard service")
                    self.show_no_data_message()
                
            except Exception as e:
                print(f"❌ Error loading real dashboard data: {e}")
                # Fallback to showing empty/default state
                self.show_no_data_message()
        else:
            print("❌ No dashboard service available")
            self.show_no_data_message()
    
    def update_metrics(self, data):
        """Update metric cards with real data"""
        try:
            # Update patient metrics
            if hasattr(self, 'patients_total_card'):
                self.update_metric_card_value(self.patients_total_card, str(data.get('total_patients', 0)))
            
            if hasattr(self, 'patients_month_card'):
                self.update_metric_card_value(self.patients_month_card, str(data.get('new_patients_month', 0)))
            
            # Update revenue metrics
            if hasattr(self, 'revenue_month_card'):
                revenue = data.get('revenue_this_month', 0)
                self.update_metric_card_value(self.revenue_month_card, f"{revenue:.0f} MAD")
            
            # Update expenses metrics
            if hasattr(self, 'expenses_month_card'):
                expenses = data.get('expenses_this_month', 0)
                self.update_metric_card_value(self.expenses_month_card, f"{expenses:.0f} MAD")
            
            # Update unpaid balance
            if hasattr(self, 'unpaid_balance_card'):
                unpaid = data.get('unpaid_balance', 0)
                self.update_metric_card_value(self.unpaid_balance_card, f"{unpaid:.0f} MAD")
                
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def show_no_data_message(self):
        """Show a message when no data is available"""
        try:
            # Create a message label if it doesn't exist
            if not hasattr(self, 'no_data_label'):
                self.no_data_label = QLabel("Aucune donnée disponible pour le moment")
                self.no_data_label.setStyleSheet("""
                    font-size: 18px;
                    color: #7f8c8d;
                    padding: 20px;
                    text-align: center;
                """)
                self.no_data_label.setAlignment(Qt.AlignCenter)
                
                # Add to layout if possible
                if hasattr(self, 'layout'):
                    self.layout().addWidget(self.no_data_label)
            
            # Show the message
            self.no_data_label.show()
            
            # Hide other widgets if they exist
            for widget in self.findChildren(QFrame) + self.findChildren(QTableWidget) + self.findChildren(FigureCanvas):
                widget.hide()
                
        except Exception as e:
            print(f"Error showing no data message: {e}")
    
    def update_metric_card_value(self, card, new_value):
        """Update the value in a metric card"""
        try:
            # Find the value label in the card and update it
            for child in card.findChildren(QLabel):
                # Look for the label with large font (value label)
                font = child.font()
                if font.pointSize() >= 24:  # This should be the value label
                    child.setText(new_value)
                    break
        except Exception as e:
            print(f"Error updating metric card: {e}")
    
    def update_revenue_chart(self, revenue_data):
        """Update the revenue chart with real data"""
        try:
            # Clear the current figure
            self.revenue_chart.figure.clear()
            
            # Create new plot
            ax = self.revenue_chart.figure.add_subplot(111)
            ax.set_title('Revenus des 6 derniers mois', fontsize=14, fontweight='bold')
            
            # Extract months and amounts from data
            months = [item.get('month', '') for item in revenue_data]
            amounts = [item.get('revenue', 0) for item in revenue_data]
            
            # Create x-axis positions
            x = range(len(months))
            
            # Create bar chart
            bars = ax.bar(x, amounts, color='#3498db', alpha=0.8, width=0.6)
            ax.set_ylabel('Revenus (MAD)')
            ax.grid(True, alpha=0.3)
            
            # Set x-ticks and labels
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars, amounts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 200,
                       f'{value:,.0f}', ha='center', va='bottom', fontsize=10)
            
            # Adjust layout to prevent label cutoff
            self.revenue_chart.figure.tight_layout()
            
            # Redraw the canvas
            self.revenue_chart.draw()
            
        except Exception as e:
            print(f"Error updating revenue chart: {e}")
    
    def update_charts(self, data):
        """Update charts with real data"""
        try:
            # Update revenue chart with real trend data
            revenue_trend = data.get('revenue_trend', [])
            if revenue_trend and hasattr(self, 'revenue_chart'):
                self.update_revenue_chart(revenue_trend)
            
            # Update expenses chart with real category data
            expenses_by_category = data.get('expenses_by_category', [])
            if expenses_by_category and hasattr(self, 'expenses_chart'):
                self.update_expenses_chart(expenses_by_category)
                
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def update_expenses_chart(self, expenses_data):
        """Update the expenses chart with real data"""
        try:
            # Clear the current figure
            self.expenses_chart.figure.clear()
            
            # Create new plot
            ax = self.expenses_chart.figure.add_subplot(111)
            ax.set_title('Répartition des Dépenses', fontsize=14, fontweight='bold')
            
            # Extract categories and amounts from data
            categories = [item.get('category', '') for item in expenses_data]
            amounts = [item.get('amount', 0) for item in expenses_data]
            
            # Calculate percentages
            total = sum(amounts) if amounts else 1
            percentages = [(amount / total * 100) if total > 0 else 0 for amount in amounts]
            
            # Colors for the pie chart
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#34495e', '#e67e22']
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(percentages, labels=categories, colors=colors[:len(categories)], 
                                             autopct='%1.1f%%', startangle=90)
            
            # Improve text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Adjust layout to prevent label cutoff
            self.expenses_chart.figure.tight_layout()
            
            # Redraw the canvas
            self.expenses_chart.draw()
            
        except Exception as e:
            print(f"Error updating expenses chart: {e}")
            
    def update_tables(self, data):
        """Update tables with real data"""
        try:
            # Update stock table if data is available
            low_stock = data.get('low_stock_items', [])
            if hasattr(self, 'stock_table'):
                self.update_stock_table_data(low_stock)
                
        except Exception as e:
            print(f"Error updating tables: {e}")
    
    def update_stock_table_data(self, low_stock_items):
        """Update stock table with real data"""
        try:
            if hasattr(self, 'stock_table'):
                self.stock_table.setRowCount(len(low_stock_items))
                
                for row, item in enumerate(low_stock_items):
                    self.stock_table.setItem(row, 0, QTableWidgetItem(item.get('name', 'N/A')))
                    self.stock_table.setItem(row, 1, QTableWidgetItem(str(item.get('current_stock', 0))))
                    self.stock_table.setItem(row, 2, QTableWidgetItem(str(item.get('min_level', 0))))
                    self.stock_table.setItem(row, 3, QTableWidgetItem('🔴 Faible'))
                    
        except Exception as e:
            print(f"Error updating stock table: {e}")
    
    def show_no_data_message(self):
        """Show message when no data is available"""
        print("ℹ️ No data available, showing empty dashboard")
    
    # Removed update_appointments_table method as it's no longer needed
    
    def update_stock_table(self):
        """Update stock alerts table"""
        # Sample data - replace with real inventory data
        stock_alerts = [
            ('Gants latex', '5', 'Stock bas'),
            ('Amalgame', '2', 'Critique'),
            ('Seringues', '15', 'Stock bas'),
            ('Anesthésique', '3', 'Critique')
        ]
        
        self.stock_table.setRowCount(len(stock_alerts))
        
        for row, (item, stock, status) in enumerate(stock_alerts):
            self.stock_table.setItem(row, 0, QTableWidgetItem(item))
            self.stock_table.setItem(row, 1, QTableWidgetItem(stock))
            
            status_item = QTableWidgetItem(status)
            if status == 'Critique':
                status_item.setBackground(QColor('#e74c3c'))
                status_item.setForeground(QColor('white'))
            elif status == 'Stock bas':
                status_item.setBackground(QColor('#f39c12'))
                status_item.setForeground(QColor('white'))
            
            self.stock_table.setItem(row, 2, status_item)
