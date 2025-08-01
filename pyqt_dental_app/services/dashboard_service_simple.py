"""
Simplified Dashboard Service
Provides mock data for dashboard functionality
"""

from datetime import datetime, timedelta
import random

class DashboardService:
    """Simplified service class for dashboard data operations"""
    
    def __init__(self):
        # Mock data initialization
        self.mock_data_initialized = True
    
    def __del__(self):
        pass
    
    # ==================== PATIENT STATISTICS ====================
    
    def get_total_patients(self):
        """Get total number of patients"""
        return 247
    
    def get_new_patients_this_month(self):
        """Get number of new patients this month"""
        return 18
    
    def get_patients_by_month(self, months=12):
        """Get patient registration trend by month"""
        results = []
        now = datetime.now()
        
        for i in range(months):
            month_date = now - timedelta(days=30 * i)
            results.append({
                'month': month_date.strftime('%b %Y'),
                'count': random.randint(10, 25)
            })
        
        return list(reversed(results))
    
    # ==================== VISIT STATISTICS ====================
    
    def get_appointments_today(self):
        """Get number of appointments today"""
        return 5
    
    def get_upcoming_appointments(self, days=7, limit=10):
        """Get upcoming appointments"""
        appointments = [
            {
                'date': datetime.now() + timedelta(hours=2),
                'time': '09:00',
                'patient_name': 'Ahmed Benali',
                'treatment': 'Consultation',
                'status': 'Programmé'
            },
            {
                'date': datetime.now() + timedelta(hours=4),
                'time': '10:30',
                'patient_name': 'Fatima Zahra',
                'treatment': 'Détartrage',
                'status': 'Programmé'
            },
            {
                'date': datetime.now() + timedelta(hours=6),
                'time': '14:00',
                'patient_name': 'Mohamed Alami',
                'treatment': 'Plombage',
                'status': 'Programmé'
            }
        ]
        return appointments[:limit]
    
    def get_visits_by_month(self, months=12):
        """Get visit statistics by month"""
        results = []
        now = datetime.now()
        
        for i in range(months):
            month_date = now - timedelta(days=30 * i)
            results.append({
                'month': month_date.strftime('%b %Y'),
                'count': random.randint(50, 120)
            })
        
        return list(reversed(results))
    
    # ==================== FINANCIAL STATISTICS ====================
    
    def get_revenue_this_month(self):
        """Get total revenue for current month"""
        return 25450.0
    
    def get_revenue_by_month(self, months=12):
        """Get revenue statistics by month"""
        results = []
        now = datetime.now()
        base_revenue = 20000
        
        for i in range(months):
            month_date = now - timedelta(days=30 * i)
            # Add some variation
            revenue = base_revenue + random.randint(-5000, 8000)
            results.append({
                'month': month_date.strftime('%b %Y'),
                'revenue': float(revenue)
            })
        
        return list(reversed(results))
    
    def get_unpaid_balance(self):
        """Get total unpaid balance"""
        return 3200.0
    
    def get_unpaid_visits(self, limit=10):
        """Get visits with unpaid balances"""
        unpaid_visits = [
            {
                'patient_name': 'Ahmed Benali',
                'visit_date': '15/07/2025',
                'total_cost': 1200.0,
                'amount_paid': 0.0,
                'balance': 1200.0,
                'treatment': 'Couronne'
            },
            {
                'patient_name': 'Fatima Zahra',
                'visit_date': '18/07/2025',
                'total_cost': 800.0,
                'amount_paid': 0.0,
                'balance': 800.0,
                'treatment': 'Détartrage'
            },
            {
                'patient_name': 'Mohamed Alami',
                'visit_date': '20/07/2025',
                'total_cost': 1500.0,
                'amount_paid': 300.0,
                'balance': 1200.0,
                'treatment': 'Implant'
            }
        ]
        return unpaid_visits[:limit]
    
    # ==================== EXPENSE STATISTICS ====================
    
    def get_expenses_this_month(self):
        """Get total expenses for current month"""
        return 8230.0
    
    def get_expenses_by_category(self, months=1):
        """Get expenses breakdown by category"""
        return [
            {'category': 'Matériel', 'amount': 2800.0, 'percentage': 34.0},
            {'category': 'Salaires', 'amount': 2300.0, 'percentage': 28.0},
            {'category': 'Loyer', 'amount': 1800.0, 'percentage': 22.0},
            {'category': 'Utilities', 'amount': 900.0, 'percentage': 11.0},
            {'category': 'Autres', 'amount': 430.0, 'percentage': 5.0}
        ]
    
    def get_expenses_by_month(self, months=12):
        """Get expense statistics by month"""
        results = []
        now = datetime.now()
        base_expense = 8000
        
        for i in range(months):
            month_date = now - timedelta(days=30 * i)
            # Add some variation
            expense = base_expense + random.randint(-2000, 3000)
            results.append({
                'month': month_date.strftime('%b %Y'),
                'expenses': float(expense)
            })
        
        return list(reversed(results))
    
    # ==================== TREATMENT STATISTICS ====================
    
    def get_popular_treatments(self, limit=10):
        """Get most popular treatments"""
        treatments = [
            {'treatment': 'Consultation', 'count': 156},
            {'treatment': 'Détartrage', 'count': 89},
            {'treatment': 'Plombage', 'count': 67},
            {'treatment': 'Extraction', 'count': 34},
            {'treatment': 'Couronne', 'count': 23},
            {'treatment': 'Implant', 'count': 15},
            {'treatment': 'Blanchiment', 'count': 12}
        ]
        return treatments[:limit]
    
    # ==================== SUMMARY METHODS ====================
    
    def get_dashboard_summary(self):
        """Get complete dashboard summary"""
        return {
            'patients': {
                'total': self.get_total_patients(),
                'new_this_month': self.get_new_patients_this_month(),
                'monthly_trend': self.get_patients_by_month(6)
            },
            'appointments': {
                'today': self.get_appointments_today(),
                'upcoming': self.get_upcoming_appointments(7, 5)
            },
            'financial': {
                'revenue_this_month': self.get_revenue_this_month(),
                'expenses_this_month': self.get_expenses_this_month(),
                'unpaid_balance': self.get_unpaid_balance(),
                'revenue_trend': self.get_revenue_by_month(6),
                'expenses_trend': self.get_expenses_by_month(6),
                'unpaid_visits': self.get_unpaid_visits(5)
            },
            'treatments': {
                'popular': self.get_popular_treatments(5)
            },
            'expenses_by_category': self.get_expenses_by_category(1)
        }
    
    def get_kpi_summary(self):
        """Get key performance indicators"""
        current_revenue = self.get_revenue_this_month()
        current_expenses = self.get_expenses_this_month()
        current_patients = self.get_new_patients_this_month()
        
        return {
            'revenue': {
                'current': current_revenue,
                'growth': 15.2
            },
            'expenses': {
                'current': current_expenses,
                'growth': -5.8
            },
            'patients': {
                'current': current_patients,
                'growth': 8.3
            },
            'profit_margin': {
                'current': ((current_revenue - current_expenses) / current_revenue * 100) if current_revenue > 0 else 0,
                'growth': 3.2
            }
        }
