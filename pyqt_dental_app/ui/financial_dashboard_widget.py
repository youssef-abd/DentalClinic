"""
Financial Dashboard Widget
Specialized dashboard for financial analytics and reporting
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
                            QComboBox, QPushButton, QDateEdit, QScrollArea,
                            QSizePolicy, QHeaderView, QTabWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
try:
    from scipy import interpolate
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ Le module scipy n'est pas installé. Certaines fonctionnalités avancées seront désactivées.")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ..services.dashboard_data_service import FinancialDashboardService

class FinancialDashboardWidget(QWidget):
    """Financial dashboard for revenue, expenses, and profit analysis"""
    
    def __init__(self, dashboard_service=None, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a scroll area for the entire content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget for the scroll area
        container = QWidget()
        container.setStyleSheet("""
            background-color: white;
        """)
        
        # Main content layout
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Set a large minimum height to ensure scrolling
        container.setMinimumHeight(2000)
        
        # Header with title
        self.create_header(content_layout)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(line)
        
        # KPI Section
        self.create_kpi_section(content_layout)
        
        # Add spacing
        content_layout.addSpacing(20)
        
        # Charts Section
        self.create_charts_section(content_layout)
        
        # Add a separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(line2)
        
        # Tables Section
        content_layout.addWidget(self.create_tables_section())
        
        # Add stretch to push content up
        content_layout.addStretch(1)
        
        # Set the container as the scroll area's widget
        scroll.setWidget(container)
        
        # Set scroll area styles
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll)
    
    def create_header(self, layout):
        """Create header with filters"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("💰 Tableau de Bord Financier")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Period selector
        period_combo = QComboBox()
        period_combo.addItems(["Ce mois", "3 derniers mois", "6 derniers mois", "Cette année"])
        period_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(period_combo)
        
        layout.addWidget(header_frame)
    
    def create_kpi_card(self, title, value, description, icon_name):
        """Create a KPI card with icon, value and description"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #3498db;
                box-shadow: 0 2px 8px rgba(52, 152, 219, 0.2);
            }
            QLabel#title {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#value {
                color: #27ae60;
                font-size: 24px;
                font-weight: bold;
                margin: 5px 0;
            }
            QLabel#description {
                color: #7f8c8d;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with icon and title
        header = QHBoxLayout()
        
        # Icon (using text as emoji for now)
        icon_label = QLabel(icon_name)
        icon_label.setStyleSheet("font-size: 20px;")
        
        title_label = QLabel(title)
        title_label.setObjectName("title")
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value")
        
        # Description
        desc_label = QLabel(description)
        desc_label.setObjectName("description")
        
        layout.addLayout(header)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        return card
        
    def update_kpi_card(self, widget, value, description, title=None):
        """Update a KPI card with new values"""
        if not widget:
            return
            
        # Find the value and description labels
        value_label = None
        desc_label = None
        title_label = None
        
        for i in range(widget.layout().count()):
            item = widget.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):  # Header layout
                for j in range(item.count()):
                    child = item.itemAt(j).widget()
                    if isinstance(child, QLabel) and child.objectName() == "title":
                        title_label = child
            elif isinstance(item.widget(), QLabel):
                if item.widget().objectName() == "value":
                    value_label = item.widget()
                elif item.widget().objectName() == "description":
                    desc_label = item.widget()
        
        # Update the values
        if value_label:
            value_label.setText(value)
        if desc_label and description:
            desc_label.setText(description)
        if title_label and title:
            title_label.setText(title)
    
    def create_kpi_section(self, layout):
        """Create the KPI section with financial metrics"""
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                border: 2px solid #e0e0e0;
                margin: 10px 0;
            }
        """)
        
        # Use a grid layout for better responsiveness
        kpi_layout = QGridLayout(kpi_frame)
        kpi_layout.setContentsMargins(10, 10, 10, 10)
        kpi_layout.setHorizontalSpacing(10)
        kpi_layout.setVerticalSpacing(10)
        
        # Revenue KPIs
        self.revenue_month = self.create_kpi_card(
            "Revenus du Mois", "0 DH", "Mois en cours", "💰")
        self.revenue_year = self.create_kpi_card(
            "Revenus Annuels", "0 DH", "Cette année", "📊")
        
        # Expenses KPIs
        self.expenses_month = self.create_kpi_card(
            "Dépenses du Mois", "0 DH", "Mois en cours", "💸")
        self.expenses_year = self.create_kpi_card(
            "Dépenses Annuelles", "0 DH", "Cette année", "📉")
        
        # Additional financial metrics
        self.profit_margin = self.create_kpi_card(
            "Marge Bénéficiaire", "0%", "Mois en cours", "📈")
        
        # Arrange KPI cards in a flexible 3-column grid to reduce width
        kpi_cards = [
            self.revenue_month,
            self.revenue_year,
            self.expenses_month,
            self.expenses_year,
            self.profit_margin,
        ]
        for idx, card in enumerate(kpi_cards):
            row = idx // 3  # 3 cards per row
            col = idx % 3
            kpi_layout.addWidget(card, row, col)

        # Stretch columns evenly
        for i in range(3):
            kpi_layout.setColumnStretch(i, 1)
        
        layout.addWidget(kpi_frame)
    
    def create_charts_section(self, layout):
        """Create the charts section with 2 charts per row"""
        # Container for charts
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(25)
        
        # First row of charts
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(15)
        
        # Revenue vs Expenses Chart
        rev_exp_widget = QWidget()
        rev_exp_widget.setStyleSheet("""
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
        """)
        rev_exp_layout = QVBoxLayout(rev_exp_widget)
        rev_exp_layout.setContentsMargins(0, 0, 0, 0)
        rev_exp_layout.addWidget(QLabel("<b>Revenus vs Dépenses</b>"))
        self.revenue_expenses_chart = self.create_revenue_expenses_chart()
        rev_exp_layout.addWidget(self.revenue_expenses_chart)
        
        # Expenses Pie Chart
        exp_pie_widget = QWidget()
        exp_pie_widget.setStyleSheet("""
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
        """)
        exp_pie_layout = QVBoxLayout(exp_pie_widget)
        exp_pie_layout.setContentsMargins(0, 0, 0, 0)
        exp_pie_layout.addWidget(QLabel("<b>Répartition des Dépenses</b>"))
        self.expenses_pie_chart = self.create_expenses_pie_chart()
        exp_pie_layout.addWidget(self.expenses_pie_chart)
        
        # Add charts to first row
        row1.addWidget(rev_exp_widget, 1)
        row1.addWidget(exp_pie_widget, 1)
        
        # Second row of charts
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(15)
        
        # Revenue Trend Chart
        rev_trend_widget = QWidget()
        rev_trend_widget.setStyleSheet("""
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
        """)
        rev_trend_layout = QVBoxLayout(rev_trend_widget)
        rev_trend_layout.setContentsMargins(0, 0, 0, 0)
        rev_trend_layout.addWidget(QLabel("<b>Tendance des Revenus</b>"))
        self.revenue_bar_chart = self.create_revenue_bar_chart()
        rev_trend_layout.addWidget(self.revenue_bar_chart)
        # Keep original trend chart off-layout for data updates
        self.revenue_trend_chart = self.create_revenue_trend_chart()
        
        # Expenses Trend Chart
        exp_trend_widget = QWidget()
        exp_trend_widget.setStyleSheet("""
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
        """)
        exp_trend_layout = QVBoxLayout(exp_trend_widget)
        exp_trend_layout.setContentsMargins(0, 0, 0, 0)
        exp_trend_layout.addWidget(QLabel("<b>Tendance des Dépenses</b>"))
        self.expenses_trend_chart = self.create_expenses_trend_chart()
        exp_trend_layout.addWidget(self.expenses_trend_chart)
        
        # Add charts to second row
        row2.addWidget(rev_trend_widget, 1)
        row2.addWidget(exp_trend_widget, 1)
        
        # Add rows to container
        container_layout.addLayout(row1)
        container_layout.addLayout(row2)
        container_layout.addStretch()
        
        # Add container to layout
        layout.addWidget(container)
        
        # Initialize chart data
        self.update_charts()

        
        # Assign figures from existing canvases
        self.expenses_figure = self.expenses_trend_chart.figure
        self.category_figure = self.expenses_pie_chart.figure
    
    def create_revenue_expenses_chart(self):
        """Create revenue vs expenses comparison chart"""
        fig = Figure(figsize=(6, 3.5), dpi=80)  # Larger size
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(280)  # Increased height
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fig.tight_layout(pad=1.5)  # Slightly more padding
        ax = fig.add_subplot(111)
        
        # Sample data - replace with real data
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        revenue = [25000, 30000, 35000, 32000, 40000, 45000]
        expenses = [18000, 22000, 25000, 23000, 28000, 30000]
        
        # Smaller bars with adjusted appearance
        bar_width = 0.3
        ax.bar([x + bar_width/2 for x in range(len(months))], revenue, width=bar_width, label='Revenus', color='#27ae60')
        ax.bar([x - bar_width/2 for x in range(len(months))], expenses, width=bar_width, label='Dépenses', color='#e74c3c')
        
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months)
        ax.set_title('Revenus vs Dépenses (6 Derniers Mois)')
        ax.legend()
        
        # Add value labels on top of bars
        for i, v in enumerate(revenue):
            ax.text(i + 0.2, v + 500, f"{v//1000}K", ha='center')
        for i, v in enumerate(expenses):
            ax.text(i - 0.2, v + 500, f"{v//1000}K", ha='center')
        
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas
    
    def create_expenses_pie_chart(self):
        """Create expenses by category pie chart"""
        fig = Figure(figsize=(6, 4.5), dpi=80)  # Increased height slightly
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(320)  # Increased height
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fig.subplots_adjust(top=0.85, bottom=0.15)  # Added padding adjustments
        ax = fig.add_subplot(111)
        
        # Sample data - replace with real data
        categories = ['Fournitures', 'Loyer', 'Salaire', 'Équipement', 'Autres']
        amounts = [15000, 25000, 45000, 20000, 10000]
        colors = ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c']
        
        # Smaller pie chart with adjusted appearance
        ax.pie(amounts, labels=categories, autopct='%1.0f%%', 
               colors=colors, startangle=90, shadow=False, 
               wedgeprops={'linewidth': 0.5}, labeldistance=0.8,
               textprops={'fontsize': 8})
        ax.axis('equal')
        ax.set_title('Répartition des Dépenses par Catégorie')
        
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas
    
    def create_revenue_trend_chart(self):
        """Create revenue trend line chart"""
        fig = Figure(figsize=(6, 3.5), dpi=80)  # Larger size
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(280)  # Increased height
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fig.tight_layout(pad=1.5)  # Slightly more padding
        ax = fig.add_subplot(111)
        
        # Sample data - replace with real data
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        revenue = [25000, 30000, 35000, 32000, 40000, 45000]
        
        ax.plot(months, revenue, marker='o', color='#27ae60', linewidth=2, markersize=8)
        ax.fill_between(months, revenue, color='#27ae60', alpha=0.1)
        ax.set_title('Évolution des Revenus (6 Derniers Mois)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add value labels on points
        for i, v in enumerate(revenue):
            ax.text(i, v + 1000, f"{v//1000}K", ha='center')
        
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas
    
    def create_revenue_bar_chart(self):
        """Create revenue bar chart for last 6 months (moved from overview)"""
        fig = Figure(figsize=(6, 4.2), dpi=80)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(336)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ax = fig.add_subplot(111)
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        amounts = [25000, 30000, 35000, 32000, 40000, 45000]
        bars = ax.bar(months, amounts, color='#3498db', alpha=0.85)
        ax.set_title('Revenus des 6 Derniers Mois')
        ax.set_ylabel('Revenus (MAD)')
        ax.grid(True, axis='y', alpha=0.3)
        for bar, val in zip(bars, amounts):
            ax.text(bar.get_x() + bar.get_width()/2., val + 200, f'{val//1000}K', ha='center')
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas



    def create_expenses_trend_chart(self):
        """Create expenses trend line chart"""
        fig = Figure(figsize=(6, 3.5), dpi=80)  # Larger size
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(280)  # Increased height
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fig.tight_layout(pad=1.5)  # Slightly more padding
        ax = fig.add_subplot(111)
        
        # Sample data - replace with real data
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        expenses = [18000, 22000, 25000, 23000, 28000, 30000]
        
        ax.plot(months, expenses, marker='o', color='#e74c3c', linewidth=2, markersize=8)
        ax.fill_between(months, expenses, color='#e74c3c', alpha=0.1)
        ax.set_title('Évolution des Dépenses (6 Derniers Mois)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add value labels on points
        for i, v in enumerate(expenses):
            ax.text(i, v + 500, f"{v//1000}K", ha='center')
        
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas
    
    def update_charts(self):
        """Update all charts with real data from dashboard service"""
        try:
            if not hasattr(self, 'dashboard_service') or not self.dashboard_service:
                print("Error: Dashboard service not available")
                return
                
            # Get real data from dashboard service
            data = self.dashboard_service.get_financial_metrics()
            
            if not data:
                print("Error: No data received from dashboard service")
                return
                
            # Update KPIs with real data
            self.update_kpis(data)
            
            # Update charts with real data
            if 'revenue_trend' in data and 'expenses_trend' in data and 'months' in data:
                self.update_revenue_vs_expenses(data)
                self.update_revenue_trend(data)
                self.update_expenses_trend(data)
                
            if 'expense_categories' in data and data['expense_categories']:
                self.update_expenses_by_category(data['expense_categories'])
            
        except Exception as e:
            print(f"Error updating charts: {e}")
            
            # Update the expenses trend chart
            self.update_expenses_trend(data)
            
        except Exception as e:
            print(f"Error updating charts: {e}")
    
    def update_revenue_vs_expenses(self, data):
        """Update the revenue vs expenses chart with real data"""
        try:
            if not hasattr(self, 'revenue_expenses_chart'):
                return
                
            fig = self.revenue_expenses_chart.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Get real data
            months = data.get('months', [])
            revenue = data.get('revenue_trend', [])
            expenses = data.get('expenses_trend', [])
            
            # If no data, show empty chart with message
            if not months or not revenue or not expenses:
                ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('Revenus vs Dépenses (Données non disponibles)')
                fig.tight_layout()
                self.revenue_expenses_chart.draw()
                return
            
            # Ensure we have matching data lengths
            min_len = min(len(months), len(revenue), len(expenses))
            months = months[:min_len]
            revenue = revenue[:min_len]
            expenses = expenses[:min_len]
            
            # Plot data with real values
            bar_width = 0.35
            x = range(len(months))
            
            ax.bar(
                [i - bar_width/2 for i in x], 
                revenue, 
                bar_width, 
                label='Revenus', 
                color='#27ae60',
                alpha=0.9
            )
            ax.bar(
                [i + bar_width/2 for i in x], 
                expenses, 
                bar_width, 
                label='Dépenses', 
                color='#e74c3c',
                alpha=0.9
            )
            
            # Customize the plot
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            ax.set_title('Revenus vs Dépenses')
            ax.legend(loc='upper left')
            
            # Format y-axis with K for thousands
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'{x/1000:.0f}K' if x > 0 else '0'
            ))
            
            # Add value labels on top of bars if there's enough space
            if len(months) <= 12:  # Only add labels if not too many bars
                for i, (rev, exp) in enumerate(zip(revenue, expenses)):
                    if rev > 0:
                        ax.text(i - bar_width/2, rev, f"{rev/1000:.0f}K", 
                               ha='center', va='bottom', fontsize=8, fontweight='bold')
                    if exp > 0:
                        ax.text(i + bar_width/2, exp, f"{exp/1000:.0f}K", 
                               ha='center', va='bottom', fontsize=8, fontweight='bold')
            
            # Add grid for better readability
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Remove top and right spines
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            
            fig.tight_layout()
            self.revenue_expenses_chart.draw()
            
        except Exception as e:
            print(f"Error updating revenue vs expenses chart: {e}")
            # Add error message to the chart
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Erreur de chargement des données', 
                       ha='center', va='center', transform=ax.transAxes, color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                fig.tight_layout()
                self.revenue_expenses_chart.draw()
            except:
                pass
    
    def update_expenses_by_category(self, categories):
        """Update the expenses by category chart with real data"""
        try:
            if not hasattr(self, 'expenses_pie_chart'):
                return
                
            fig = self.expenses_pie_chart.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # If no categories data, show empty chart with message
            if not categories:
                ax.text(0.5, 0.5, 'Aucune donnée de catégorie disponible', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('Répartition des Dépenses (Données non disponibles)')
                fig.tight_layout()
                self.expenses_pie_chart.draw()
                return
            
            # Extract category names and amounts, filter out zero amounts
            filtered_categories = [
                cat for cat in categories 
                if isinstance(cat, dict) and 'name' in cat and 'amount' in cat and cat['amount'] > 0
            ]
            
            if not filtered_categories:
                ax.text(0.5, 0.5, 'Aucune dépense à afficher', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('Aucune Dépense')
                fig.tight_layout()
                self.expenses_pie_chart.draw()
                return
                
            labels = [str(cat['name']) for cat in filtered_categories]
            amounts = [float(cat['amount']) for cat in filtered_categories]
            
            # Sort categories by amount (descending)
            sorted_data = sorted(zip(amounts, labels), reverse=True)
            amounts, labels = zip(*sorted_data) if sorted_data else ([], [])
            
            # Define a color palette
            colors = plt.cm.tab20c(range(len(amounts)))
            
            # Create the pie chart
            wedges, texts, autotexts = ax.pie(
                amounts,
                labels=labels,
                autopct=lambda p: f'{p:.0f}%' if p >= 5 else '',
                startangle=90,
                wedgeprops={'linewidth': 0.8, 'edgecolor': 'white'},
                textprops={'fontsize': 8},
                pctdistance=0.8,
                labeldistance=1.05,
                colors=colors
            )
            
            # Add a circle in the center to make it a donut chart
            centre_circle = plt.Circle((0, 0), 0.6, fc='white')
            ax.add_artist(centre_circle)
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            ax.set_title('Répartition des Dépenses par Catégorie')
            
            # Adjust the layout to make room for the legend
            plt.subplots_adjust(left=0.1, right=0.7, top=0.9, bottom=0.1)
            
            # Format amounts with thousands separator
            formatted_amounts = [f"{amount:,.0f} DH" for amount in amounts]
            
            # Add a legend to the right of the chart
            legend = ax.legend(
                wedges,
                [f"{label}: {amount}" for label, amount in zip(labels, formatted_amounts)],
                title="Détails des Dépenses",
                loc="center left",
                bbox_to_anchor=(0.9, 0, 0.5, 1),
                fontsize=8,
                frameon=False
            )
            
            # Make the legend title bold
            legend.set_title(legend.get_title().get_text(), prop={'weight': 'bold'})
            
            # Add total in the center of the donut
            total = sum(amounts)
            ax.text(0, 0, f"Total\n{total:,.0f} DH", 
                   ha='center', va='center', 
                   fontsize=10, fontweight='bold')
            
            fig.tight_layout()
            self.expenses_pie_chart.draw()
            
        except Exception as e:
            print(f"Error updating expenses by category chart: {e}")
            # Add error message to the chart
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Erreur de chargement des données', 
                       ha='center', va='center', transform=ax.transAxes, color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                fig.tight_layout()
                self.expenses_pie_chart.draw()
            except:
                pass
    
    def update_revenue_trend(self, data):
        """Update the revenue trend chart with real data"""
        try:
            if not hasattr(self, 'revenue_trend_chart'):
                return
                
            fig = self.revenue_trend_chart.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Get real data
            months = data.get('months', [])
            revenue = data.get('revenue_trend', [])
            
            # If no data, show empty chart with message
            if not months or not revenue:
                ax.text(0.5, 0.5, 'Aucune donnée de tendance disponible', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('Tendance des Revenus (Données non disponibles)')
                fig.tight_layout()
                self.revenue_trend_chart.draw()
                return
            
            # Ensure we have matching data lengths
            min_len = min(len(months), len(revenue))
            months = months[:min_len]
            revenue = revenue[:min_len]
            
            # Plot a smooth line if scipy is available
            if SCIPY_AVAILABLE and len(months) > 1:
                try:
                    x = np.arange(len(months))
                    x_new = np.linspace(0, len(months)-1, 300)
                    
                    # Cubic spline interpolation for smooth curve
                    spl = interpolate.make_interp_spline(x, revenue, k=min(3, len(months)-1))
                    revenue_smooth = spl(x_new)
                    
                    # Plot the smooth curve
                    ax.plot(x_new, revenue_smooth, '-', color='#27ae60', linewidth=2, alpha=0.3)
                except Exception as e:
                    print(f"⚠️ Erreur lors du lissage de la courbe: {e}")
                    # Fall back to normal line plot if smoothing fails
                    ax.plot(months, revenue, 'o-', color='#27ae60', linewidth=2, markersize=8,
                          markerfacecolor='white', markeredgewidth=2, markeredgecolor='#27ae60')
            
            # Plot the actual data points
            line, = ax.plot(months, revenue, 'o-', color='#27ae60', linewidth=2, markersize=8,
                          markerfacecolor='white', markeredgewidth=2, markeredgecolor='#27ae60')
            
            # Fill under the line
            ax.fill_between(months, revenue, color='#27ae60', alpha=0.1)
            
            # Customize the plot
            ax.set_title('Tendance des Revenus')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Format y-axis with K for thousands
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'{x/1000:.0f}K' if x > 0 else '0'
            ))
            
            # Add value labels on points if not too many
            if len(months) <= 12:  # Only add labels if not too many points
                for i, (m, v) in enumerate(zip(months, revenue)):
                    if v > 0:  # Only show label if value is positive
                        ax.text(i, v, f"{v/1000:.0f}K", 
                               ha='center', va='bottom', 
                               fontsize=8, fontweight='bold')
            
            # Remove top and right spines
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            
            fig.tight_layout()
            self.revenue_trend_chart.draw()
            
        except Exception as e:
            print(f"Error updating revenue trend chart: {e}")
            # Add error message to the chart
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Erreur de chargement des données', 
                       ha='center', va='center', transform=ax.transAxes, color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                fig.tight_layout()
                self.revenue_trend_chart.draw()
            except:
                pass
            
    def update_expenses_trend(self, data):
        """Update the expenses trend chart with real data"""
        try:
            if not hasattr(self, 'expenses_trend_chart'):
                return
                
            fig = self.expenses_trend_chart.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Get real data
            months = data.get('months', [])
            expenses = data.get('expenses_trend', [])
            
            # If no data, show empty chart with message
            if not months or not expenses:
                ax.text(0.5, 0.5, 'Aucune donnée de tendance disponible', 
                       ha='center', va='center', transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title('Tendance des Dépenses (Données non disponibles)')
                fig.tight_layout()
                self.expenses_trend_chart.draw()
                return
            
            # Ensure we have matching data lengths
            min_len = min(len(months), len(expenses))
            months = months[:min_len]
            expenses = expenses[:min_len]
            
            # Plot a smooth line if scipy is available
            if SCIPY_AVAILABLE and len(months) > 1:
                try:
                    x = np.arange(len(months))
                    x_new = np.linspace(0, len(months)-1, 300)
                    
                    # Cubic spline interpolation for smooth curve
                    spl = interpolate.make_interp_spline(x, expenses, k=min(3, len(months)-1))
                    expenses_smooth = spl(x_new)
                    
                    # Plot the smooth curve
                    ax.plot(x_new, expenses_smooth, '-', color='#e74c3c', linewidth=2, alpha=0.3)
                except Exception as e:
                    print(f"⚠️ Erreur lors du lissage de la courbe: {e}")
                    # Fall back to normal line plot if smoothing fails
                    ax.plot(months, expenses, 'o-', color='#e74c3c', linewidth=2, markersize=8,
                          markerfacecolor='white', markeredgewidth=2, markeredgecolor='#e74c3c')
            
            # Plot the actual data points
            line, = ax.plot(months, expenses, 'o-', color='#e74c3c', linewidth=2, markersize=8,
                          markerfacecolor='white', markeredgewidth=2, markeredgecolor='#e74c3c')
            
            # Fill under the line
            ax.fill_between(months, expenses, color='#e74c3c', alpha=0.1)
            
            # Customize the plot
            ax.set_title('Tendance des Dépenses')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Format y-axis with K for thousands
            ax.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'{x/1000:.0f}K' if x > 0 else '0'
            ))
            
            # Add value labels on points if not too many
            if len(months) <= 12:  # Only add labels if not too many points
                for i, (m, v) in enumerate(zip(months, expenses)):
                    if v > 0:  # Only show label if value is positive
                        ax.text(i, v, f"{v/1000:.0f}K", 
                               ha='center', va='bottom', 
                               fontsize=8, fontweight='bold')
            
            # Remove top and right spines
            for spine in ['top', 'right']:
                ax.spines[spine].set_visible(False)
            
            fig.tight_layout()
            self.expenses_trend_chart.draw()
            
        except Exception as e:
            print(f"Error updating expenses trend chart: {e}")
            # Add error message to the chart
            try:
                fig.clear()
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Erreur de chargement des données', 
                       ha='center', va='center', transform=ax.transAxes, color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                fig.tight_layout()
                self.expenses_trend_chart.draw()
            except:
                pass
    
    def create_profit_chart(self):
        """Create profit trend chart"""
        fig = Figure(figsize=(16, 10), dpi=120)
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(600)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        ax = fig.add_subplot(111)
        ax.set_title('Évolution du Bénéfice', fontweight='bold')
        
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin']
        profits = [14000, 15500, 10800, 19200, 21800, 17220]
        
        ax.plot(months, profits, marker='o', linewidth=3, color='#3498db', markersize=8)
        ax.fill_between(months, profits, alpha=0.3, color='#3498db')
        
        ax.set_ylabel('Bénéfice (MAD)')
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for i, profit in enumerate(profits):
            ax.annotate(f'{profit:,}', (i, profit), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontsize=9)
        
        fig.tight_layout(pad=3.0)  # Increased padding
        return canvas
    
    def create_tables_section(self):
        tables_layout = QVBoxLayout()
        tables_container = QWidget()
        tables_container.setLayout(tables_layout)
        return tables_container
    

    



    
    def load_data(self):
        """Load data for the dashboard"""
        try:
            if not self.dashboard_service:
                return
                
            # Load complete financial metrics
            financial_metrics = self.dashboard_service.get_financial_metrics()
            
            # Load additional data
            expenses_summary = self.dashboard_service.get_expenses_summary(months=6)
            expenses_trend = self.dashboard_service.get_expenses_trend(months=6)
            
            # Update KPIs with complete financial data
            self.update_kpis(financial_metrics)
            
            # Update charts
            self.update_expenses_chart(expenses_trend)
            self.update_expenses_by_category(expenses_summary.get('categories', []))
            
            # Update revenue vs expenses chart
            self.update_revenue_vs_expenses(financial_metrics)
            
            # Update revenue trend chart
            self.update_revenue_trend(financial_metrics)
            
        except Exception as e:
            print(f"Error loading financial data: {e}")
            
    def refresh_data(self):
        """Refresh data from the service"""
        service = FinancialDashboardService()
        try:
            data = service.get_financial_overview()
            # Update UI elements with data
            self.update_kpis(data)
            self.update_charts()
        finally:
            service.close()
    
    def update_kpis(self, data):
        """Update the KPI cards with expense data"""
        try:
            # Update revenue KPIs
            self.update_kpi_card(self.revenue_month, 
                              f"{data.get('revenue_month', 0):,.2f} DH", 
                              "Mois en cours")
            
            self.update_kpi_card(self.revenue_year, 
                              f"{data.get('revenue_year', 0):,.2f} DH", 
                              "Cette année")
            
            # Update expenses KPIs
            self.update_kpi_card(self.expenses_month, 
                              f"{data.get('expenses_month', 0):,.2f} DH", 
                              "Mois en cours")
            
            self.update_kpi_card(self.expenses_year, 
                              f"{data.get('expenses_year', 0):,.2f} DH", 
                              "Cette année")
            
            # Update profit margin KPI
            profit_margin = data.get('profit_margin', 0)
            self.update_kpi_card(self.profit_margin, 
                              f"{profit_margin:.1f}%", 
                              "Mois en cours")
            
            # # Update other KPIs
            # self.update_kpi_card(self.expenses_by_category, 
            #                   "Voir graphique", 
            #                   f"{len(data.get('expense_categories', []))} catégories")
            
            # self.update_kpi_card(self.revenue_trend, 
            #                   "Voir graphique", 
            #                   f"Tendance sur {data.get('trend_months', 6)} mois")
            
            # self.update_kpi_card(self.expenses_trend, 
            #                   "Voir graphique", 
            #                   f"Tendance sur {data.get('trend_months', 6)} mois")
            
        except Exception as e:
            print(f"Error updating KPIs: {e}")
    
    def update_expenses_chart(self, data):
        """Update the expenses trend chart"""
        try:
            # Clear previous figure
            self.expenses_figure.clear()
            
            if not data:
                return
                
            # Prepare data
            months = [item['month'] for item in data]
            amounts = [item['amount'] for item in data]
            
            # Create bar chart with adjusted layout
            self.expenses_figure.clear()
            ax = self.expenses_figure.subplots()
            
            # Plot data
            x = range(len(months))
            bars = ax.bar(x, amounts, color='#2ecc71', width=0.6)
            
            # Customize x-axis
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45, ha='right')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only show label if height is greater than 0
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f} DH',
                            ha='center', va='bottom')
            
            # Customize chart
            ax.set_title('Dépenses des 6 Derniers Mois', fontweight='bold', pad=20)
            ax.set_ylabel('Montant (DH)', labelpad=10)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only show label if height is greater than 0
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f} DH',
                            ha='center', va='bottom')
            
            # Update the canvas
            self.expenses_trend_chart.draw()
            
        except Exception as e:
            print(f"Error updating expenses chart: {e}")
    
    def update_expenses_by_category(self, categories):
        """Update the expenses by category chart"""
        try:
            # Clear previous figure
            self.category_figure.clear()
            
            if not categories:
                return
                
            # Prepare data
            labels = [item['category'] for item in categories]
            amounts = [item['amount'] for item in categories]
            
            # Create pie chart with adjusted layout
            self.category_figure.clear()
            ax = self.category_figure.subplots()
            
            # Create pie chart with tight layout
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=labels,
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops=dict(width=0.4, edgecolor='w'),
                colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],
                pctdistance=0.85,
                labeldistance=1.1
            )
            
            # Style the percentages
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Add a circle in the center to make it a donut chart
            centre_circle = plt.Circle((0,0), 0.2, fc='white')
            ax.add_artist(centre_circle)
            
            # Add total amount in the center
            total = sum(amounts)
            ax.text(0, 0, f"Total\n{total:,.0f} DH", 
                   ha='center', va='center', 
                   fontsize=12, fontweight='bold')
            
            ax.set_title('Répartition des Dépenses par Catégorie', fontweight='bold', pad=20)
            
            # Update the canvas
            self.expenses_pie_chart.draw()
            
        except Exception as e:
            print(f"Error updating category chart: {e}")
