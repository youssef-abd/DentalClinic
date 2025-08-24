"""
Patient Dashboard Widget
Analytics and insights about patient management
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
                            QProgressBar, QPushButton, QScrollArea, QSizePolicy,
                            QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta, date
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Use a non-interactive backend to avoid threading issues
matplotlib.use('Agg')

from ..services.dashboard_service_real import RealDashboardService
from sqlalchemy import func
from ..models.database import DatabaseManager, Patient

class PatientDashboardWidget(QWidget):
    """Patient analytics dashboard"""
    
    def __init__(self, dashboard_service=None, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service or RealDashboardService()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container widget for the scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)
        
        # Set the container as the scroll area's widget
        scroll.setWidget(container)
        
        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Header
        self.create_header(layout)
        
        # Patient metrics
        self.create_metrics_section(layout)
        
        # Charts section
        self.create_charts_section(layout)
        
        # Patient insights in a scrollable area
        insights_scroll = QScrollArea()
        insights_scroll.setWidgetResizable(True)
        insights_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        insights_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        insights_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        insights_container = QWidget()
        insights_layout = QVBoxLayout(insights_container)
        insights_layout.setContentsMargins(10, 10, 10, 10)
        insights_layout.setSpacing(20)
        
        self.create_insights_section(insights_layout)
        
        insights_scroll.setWidget(insights_container)
        layout.addWidget(insights_scroll, 1)  # Add stretch factor to make it expand
    
    def create_header(self, layout):
        """Create header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #9b59b6);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("Tableau de Bord Patients")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
    
    def create_metrics_section(self, layout):
        """Create patient metrics cards matching financial dashboard style"""
        # Create a container frame with a light background matching financial dashboard
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                border: 2px solid #e0e0e0;
                margin: 10px 0;
            }
        """)
        
        # Use a grid layout for metrics to match financial dashboard (3 per row)
        kpi_layout = QGridLayout(metrics_frame)
        kpi_layout.setContentsMargins(10, 10, 10, 10)
        kpi_layout.setHorizontalSpacing(10)
        kpi_layout.setVerticalSpacing(10)
        
        # Metrics data (will be updated with real data)
        metrics = [
            {'title': 'Total', 'value': '0', 'description': 'Patients enregistrés', 'icon': '', 'color': '#3498db'},
            {'title': 'Ce Mois', 'value': '0', 'description': 'Nouveaux patients', 'icon': '', 'color': '#2ecc71'},
            {'title': 'Par Mois', 'value': '0', 'description': 'Moyenne mensuelle', 'icon': '', 'color': '#9b59b6'},
            {'title': 'Par An', 'value': '0', 'description': 'Moyenne annuelle', 'icon': '', 'color': '#e74c3c'},
            {'title': 'Récents', 'value': '0', 'description': '7 derniers jours', 'icon': '', 'color': '#f39c12'}
        ]
        
        # Create metric cards
        for idx, metric in enumerate(metrics):
            card = self.create_kpi_card(
                metric['title'],
                metric['value'],
                metric['description'],
                metric['icon'],
                metric['color']
            )
            if not hasattr(self, 'metric_cards'):
                self.metric_cards = []
            self.metric_cards.append(card)
            row = idx // 3
            col = idx % 3
            kpi_layout.addWidget(card, row, col)
        
        # Stretch columns evenly
        for i in range(3):
            kpi_layout.setColumnStretch(i, 1)
        
        layout.addWidget(metrics_frame)
    
    def create_kpi_card(self, title, value, description, icon_name, color):
        """Create a professional KPI card matching financial dashboard style"""
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
        header.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("title")
        
        if icon_name:
            # Icon
            icon_label = QLabel(icon_name)
            icon_label.setStyleSheet(f"""
                font-size: 20px;
                color: {color};
                font-weight: bold;
            """)
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
        
        # expose value label for updates
        card.value_label = value_label
        return card
    
    def create_metric_card(self, title, value, icon, color):
        """Create a metric card"""
        card = QFrame()
        card.setFixedHeight(150)  # Increased height
        card.setMinimumWidth(280)  # Added minimum width
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border-left: 5px solid {color};
                padding: 20px;
                margin: 5px;
                border: 1px solid #e0e0e0;
            }}
            QFrame:hover {{
                border: 1px solid #b3b3b3;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)  # Added margins
        layout.setSpacing(15)  # Added spacing
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 36px;
            background-color: {color}20;
            border-radius: 30px;
            padding: 15px;
            min-width: 60px;
            max-width: 60px;
            min-height: 60px;
            max-height: 60px;
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)  # Increased spacing
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #7f8c8d; font-weight: 500; margin-bottom: 5px;")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; margin: 5px 0px;")
        value_label.setWordWrap(True)
        text_layout.addWidget(value_label)
        
        text_layout.addStretch()
        layout.addLayout(text_layout)
        
        return card
    
    def create_charts_section(self, layout):
        """Create charts section with proper scrolling"""
        # Container for charts with fixed height
        charts_container = QFrame()
        charts_container.setStyleSheet("background: transparent;")
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setSpacing(20)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        
        # Set fixed height for charts
        chart_height = 400  # Increased height for better visibility
        
        # Only keep the registration chart
        self.reg_chart = self.create_registration_chart()
        self.reg_chart.setMinimumHeight(chart_height)
        self.reg_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        charts_layout.addWidget(self.reg_chart, 1)
        
        layout.addWidget(charts_container)
    
    def create_registration_chart(self):
        """Create patient registration trend chart"""
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.set_title('Nouveaux Patients par Mois', fontweight='bold')
        ax.text(0.5, 0.5, 'Chargement des données...', ha='center', va='center', transform=ax.transAxes, color='#666')
        ax.set_ylabel('Nouveaux Patients')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        return canvas
    
    def create_gender_distribution_chart(self):
        """Create gender distribution chart with error handling"""
        try:
            fig = Figure(figsize=(6, 4), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.set_title('Répartition par Genre', fontweight='bold')
            
            # Use only real data; no defaults
            genders = []
            counts = []
            colors = ['#3498db', '#e83e8c', '#6c757d']
            
            # Try to get real data if service is available
            if hasattr(self, 'dashboard_service') and self.dashboard_service:
                try:
                    gender_data = self.dashboard_service.get_patient_gender_distribution()
                    if gender_data and any(isinstance(v, (int, float)) and v > 0 for v in gender_data.values()):
                        # Filter out zero counts for better visualization
                        filtered_data = {k: v for k, v in gender_data.items() if v and v > 0}
                        if filtered_data:  # Only update if we have valid data
                            genders = list(filtered_data.keys())
                            counts = [max(0, float(v)) for v in filtered_data.values()]
                            # Ensure we have the same number of colors as data points
                            colors = colors[:len(genders)]
                except Exception as e:
                    print(f"Error loading gender data: {e}")
            
            # Only create the pie chart if we have positive values
            if any(count > 0 for count in counts):
                # Create donut chart with error handling
                try:
                    wedges, texts, autotexts = ax.pie(
                        counts, 
                        labels=genders if len(genders) == len(counts) else None,
                        colors=colors,
                        autopct='%1.1f%%', 
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor='w')
                    )
                    
                    # Style the percentages if they exist
                    for autotext in autotexts:
                        autotext.set_color('white' if max(counts) > 0 else '#333333')
                        autotext.set_fontweight('bold')
                    
                    # Add a circle in the center to make it a donut chart
                    centre_circle = plt.Circle((0,0), 0.2, fc='white')
                    ax.add_artist(centre_circle)
                    
                    # Add total count in the center
                    total = int(sum(counts))
                    ax.text(0, 0, f"Total\n{total}", ha='center', va='center', 
                           fontsize=12, fontweight='bold', color='#2c3e50')
                    
                except (ValueError, ZeroDivisionError) as e:
                    print(f"Error creating pie chart: {e}")
                    ax.text(0.5, 0.5, 'Données non disponibles', 
                           ha='center', va='center', fontsize=12, color='#666')
            else:
                # Show message if no data is available
                ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                       ha='center', va='center', fontsize=12, color='#666')
            
            fig.tight_layout()
            return canvas
            
        except Exception as e:
            print(f"Unexpected error in create_gender_distribution_chart: {e}")
            # Return an empty canvas in case of any error
            fig = Figure(figsize=(6, 4), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 'Erreur de chargement', 
                   ha='center', va='center', fontsize=12, color='#e74c3c')
            return canvas
        
    def create_age_distribution_chart(self):
        """Create age distribution chart (real data only)"""
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        ax.set_title('Répartition par Âge', fontweight='bold')
        
        # Compute from database
        try:
            session, owned = self._get_session()
            rows = session.query(Patient.date_naissance).filter(Patient.date_naissance.isnot(None)).all()
            age_counts = {'0-18': 0, '19-35': 0, '36-50': 0, '51-65': 0, '65+': 0}
            today = date.today()
            for (dob,) in rows:
                try:
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    if age <= 18:
                        age_counts['0-18'] += 1
                    elif age <= 35:
                        age_counts['19-35'] += 1
                    elif age <= 50:
                        age_counts['36-50'] += 1
                    elif age <= 65:
                        age_counts['51-65'] += 1
                    else:
                        age_counts['65+'] += 1
                except Exception:
                    continue
            labels = list(age_counts.keys())
            counts = list(age_counts.values())
        except Exception as e:
            print(f"Error loading age distribution: {e}")
            labels, counts = [], []
        finally:
            try:
                if 'owned' in locals() and owned:
                    session.close()
            except Exception:
                pass
        
        if counts and any(c > 0 for c in counts):
            colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
            wedges, texts, autotexts = ax.pie(counts, labels=labels, colors=colors,
                                             autopct='%1.1f%%', startangle=90,
                                             wedgeprops=dict(width=0.4, edgecolor='w'))
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            total = sum(counts)
            centre_circle = plt.Circle((0,0), 0.2, fc='white')
            ax.add_artist(centre_circle)
            ax.text(0, 0, f"Total\n{total}", ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='#2c3e50')
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                    ha='center', va='center', fontsize=12, color='#666')
        
        fig.tight_layout()
        return canvas
    
    def create_insights_section(self, layout):
        """Create patient insights section"""
        # This method is kept as a placeholder in case we want to add other insights later
        pass

    def _get_session(self):
        """Return a SQLAlchemy session and whether we own it"""
        try:
            if hasattr(self, 'dashboard_service') and hasattr(self.dashboard_service, 'session') and self.dashboard_service.session:
                return self.dashboard_service.session, False
        except Exception:
            pass
        dbm = DatabaseManager()
        return dbm.get_session(), True

    def _month_labels_and_counts(self, months=6):
        """Compute month labels and patient registration counts for the last N months"""
        session, owned = self._get_session()
        try:
            # Build list of (year, month) for last N months oldest->newest
            today = date.today()
            ym_list = []
            y, m = today.year, today.month
            for i in range(months - 1, -1, -1):
                yy, mm = y, m
                for _ in range(i):
                    if mm == 1:
                        yy -= 1
                        mm = 12
                    else:
                        mm -= 1
                ym_list.append((yy, mm))

            # Start date = first day of first month in range
            start_year, start_month = ym_list[0]
            start_date = date(start_year, start_month, 1)

            # Query counts grouped by year-month using SQLite strftime
            rows = session.query(
                func.strftime('%Y-%m', Patient.created_at).label('ym'),
                func.count(Patient.id)
            ).filter(
                Patient.created_at >= start_date
            ).group_by('ym').all()
            counts_by_ym = {row[0]: int(row[1] or 0) for row in rows}

            french_months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            labels = []
            counts = []
            for yy, mm in ym_list:
                ym_key = f"{yy}-{mm:02d}"
                labels.append(french_months[mm - 1])
                counts.append(int(counts_by_ym.get(ym_key, 0)))
            return labels, counts
        finally:
            if owned:
                session.close()
    
    def load_data(self):
        """Load patient data from the real database"""
        try:
            session, owned = self._get_session()

            # Total patients
            total_patients = session.query(func.count(Patient.id)).scalar() or 0

            # New patients this month
            month_start = date(datetime.now().year, datetime.now().month, 1)
            new_patients = session.query(func.count(Patient.id)).filter(
                Patient.created_at >= month_start
            ).scalar() or 0

            # Monthly and annual averages from grouped trend data
            _, counts6 = self._month_labels_and_counts(months=6)
            monthly_avg = int(round(sum(counts6) / max(1, len(counts6)))) if counts6 else 0

            _, counts12 = self._month_labels_and_counts(months=12)
            annual_avg = int(round(sum(counts12) / max(1, len(counts12)))) if counts12 else 0

            # Recent (last 7 days)
            recent_start = (datetime.now() - timedelta(days=7)).date()
            recent_7_days = session.query(func.count(Patient.id)).filter(
                Patient.created_at >= recent_start
            ).scalar() or 0

            # Update metric cards: Total, Ce Mois, Par Mois, Par An, Récents
            if hasattr(self, 'metric_cards') and len(self.metric_cards) >= 5:
                values = [total_patients, new_patients, monthly_avg, annual_avg, recent_7_days]
                for idx, val in enumerate(values):
                    self.metric_cards[idx].value_label.setText(str(int(val)))

            # Update registration chart
            self.update_registration_chart()

        except Exception as e:
            print(f"Error loading patient data: {e}")
        finally:
            try:
                if owned:
                    session.close()
            except Exception:
                pass

    def update_registration_chart(self):
        """Update the registration chart with real data"""
        try:
            # Compute grouped data directly from DB
            months, counts = self._month_labels_and_counts(months=6)

            fig = self.reg_chart.figure
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_title('Nouveaux Patients par Mois', fontweight='bold')
            ax.set_ylabel('Nouveaux Patients')
            ax.grid(True, alpha=0.3)

            if counts and any(c > 0 for c in counts):
                ax.plot(months, counts, marker='o', linewidth=3, color='#8e44ad', markersize=8)
                ax.fill_between(months, counts, alpha=0.3, color='#8e44ad')
                for i, count in enumerate(counts):
                    ax.annotate(str(count), (i, count), textcoords="offset points",
                                xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Aucune donnée disponible', ha='center', va='center', transform=ax.transAxes, color='#666')

            fig.tight_layout()
            self.reg_chart.draw()

        except Exception as e:
            print(f"Error updating registration chart: {e}")
