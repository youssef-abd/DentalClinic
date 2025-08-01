"""
Dashboard Service
Handles dashboard data aggregation and statistics
"""

from datetime import datetime, timedelta, date
from sqlalchemy import func, extract, and_, case, Date, desc
from sqlalchemy.orm import Session

try:
    from ..models.database import Patient, Visit, User, DatabaseManager
    from ..models.expense_models import Expense, ExpenseCategory
    from ..models.inventory_models import InventoryItem, InventoryTransaction
    MODELS_AVAILABLE = True
except ImportError:
    # Fallback if models are not available
    Patient = Visit = User = Expense = ExpenseCategory = InventoryItem = InventoryTransaction = DatabaseManager = None
    MODELS_AVAILABLE = False
    print("Warning: Some models not available for dashboard service")

class DashboardService:
    """Service class for dashboard data operations"""
    
    def __init__(self):
        self.session = Session()
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    # ==================== PATIENT STATISTICS ====================
    
    def get_total_patients(self):
        """Get total number of patients"""
        try:
            return self.session.query(Patient).count()
        except Exception as e:
            print(f"Error getting total patients: {e}")
            return 0
    
    def get_new_patients_this_month(self):
        """Get number of new patients this month"""
        try:
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            return self.session.query(Patient).filter(
                Patient.created_at >= month_start
            ).count()
        except Exception as e:
            print(f"Error getting new patients this month: {e}")
            return 0
    
    def get_patients_by_month(self, months=12):
        """Get patient registration trend by month"""
        try:
            results = []
            now = datetime.now()
            
            for i in range(months):
                month_date = now - timedelta(days=30 * i)
                month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                if i == 0:
                    month_end = now
                else:
                    next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                    month_end = next_month - timedelta(days=1)
                
                count = self.session.query(Patient).filter(
                    and_(Patient.created_at >= month_start, Patient.created_at <= month_end)
                ).count()
                
                results.append({
                    'month': month_start.strftime('%b %Y'),
                    'count': count
                })
            
            return list(reversed(results))
        except Exception as e:
            print(f"Error getting patients by month: {e}")
            return []
    
    # ==================== VISIT STATISTICS ====================
    
    def get_appointments_today(self):
        """Get number of appointments today"""
        try:
            today = datetime.now().date()
            return self.session.query(Visit).filter(
                func.date(Visit.visit_date) == today
            ).count()
        except Exception as e:
            print(f"Error getting appointments today: {e}")
            return 0
    
    def get_upcoming_appointments(self, days=7, limit=10):
        """Get upcoming appointments"""
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            
            appointments = self.session.query(Visit).join(Patient).filter(
                and_(Visit.visit_date >= start_date, Visit.visit_date <= end_date)
            ).order_by(Visit.visit_date).limit(limit).all()
            
            return [{
                'date': visit.visit_date,
                'time': visit.visit_date.strftime('%H:%M') if visit.visit_date else 'N/A',
                'patient_name': f"{visit.patient.first_name} {visit.patient.last_name}" if visit.patient else 'N/A',
                'treatment': visit.treatment_description or 'Consultation',
                'status': getattr(visit, 'status', 'Programmé')
            } for visit in appointments]
        except Exception as e:
            print(f"Error getting upcoming appointments: {e}")
            return []
    
    def get_visits_by_month(self, months=12):
        """Get visit statistics by month"""
        try:
            results = []
            now = datetime.now()
            
            for i in range(months):
                month_date = now - timedelta(days=30 * i)
                month_start = month_date.replace(day=1)
                
                if i == 0:
                    month_end = now
                else:
                    next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                    month_end = next_month - timedelta(days=1)
                
                count = self.session.query(Visit).filter(
                    and_(Visit.visit_date >= month_start, Visit.visit_date <= month_end)
                ).count()
                
                results.append({
                    'month': month_start.strftime('%b %Y'),
                    'count': count
                })
            
            return list(reversed(results))
        except Exception as e:
            print(f"Error getting visits by month: {e}")
            return []
    
    # ==================== FINANCIAL STATISTICS ====================
    
    def get_revenue_this_month(self):
        """Get total revenue for current month"""
        try:
            now = datetime.now()
            month_start = now.replace(day=1)
            
            total = self.session.query(func.sum(Visit.amount_paid)).filter(
                and_(Visit.visit_date >= month_start, Visit.amount_paid.isnot(None))
            ).scalar()
            
            return float(total) if total else 0.0
        except Exception as e:
            print(f"Error getting revenue this month: {e}")
            return 0.0
    
    def get_revenue_by_month(self, months=12):
        """Get revenue statistics by month"""
        try:
            results = []
            now = datetime.now()
            
            for i in range(months):
                month_date = now - timedelta(days=30 * i)
                month_start = month_date.replace(day=1)
                
                if i == 0:
                    month_end = now
                else:
                    next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                    month_end = next_month - timedelta(days=1)
                
                total = self.session.query(func.sum(Visit.amount_paid)).filter(
                    and_(Visit.visit_date >= month_start, 
                         Visit.visit_date <= month_end,
                         Visit.amount_paid.isnot(None))
                ).scalar()
                
                results.append({
                    'month': month_start.strftime('%b %Y'),
                    'revenue': float(total) if total else 0.0
                })
            
            return list(reversed(results))
        except Exception as e:
            print(f"Error getting revenue by month: {e}")
            return []
    
    def get_unpaid_balance(self):
        """Get total unpaid balance"""
        try:
            total_cost = self.session.query(func.sum(Visit.total_cost)).filter(
                Visit.total_cost.isnot(None)
            ).scalar() or 0.0
            
            total_paid = self.session.query(func.sum(Visit.amount_paid)).filter(
                Visit.amount_paid.isnot(None)
            ).scalar() or 0.0
            
            return float(total_cost - total_paid)
        except Exception as e:
            print(f"Error getting unpaid balance: {e}")
            return 0.0
    
    def get_unpaid_visits(self, limit=10):
        """Get visits with unpaid balances"""
        try:
            unpaid_visits = self.session.query(Visit).join(Patient).filter(
                Visit.total_cost > Visit.amount_paid
            ).order_by(Visit.visit_date.desc()).limit(limit).all()
            
            return [{
                'patient_name': f"{visit.patient.first_name} {visit.patient.last_name}" if visit.patient else 'N/A',
                'visit_date': visit.visit_date.strftime('%d/%m/%Y') if visit.visit_date else 'N/A',
                'total_cost': visit.total_cost or 0.0,
                'amount_paid': visit.amount_paid or 0.0,
                'balance': (visit.total_cost or 0.0) - (visit.amount_paid or 0.0),
                'treatment': visit.treatment_description or 'N/A'
            } for visit in unpaid_visits]
        except Exception as e:
            print(f"Error getting unpaid visits: {e}")
            return []
    
    # ==================== EXPENSE STATISTICS ====================
    
    def get_expenses_this_month(self):
        """Get total expenses for current month"""
        try:
            now = datetime.now()
            month_start = now.replace(day=1).date()
            month_end = now.date()
            
            total = self.session.query(func.sum(Expense.amount)).filter(
                and_(Expense.date >= month_start, 
                     Expense.date <= month_end)
            ).scalar()
            
            return float(total) if total else 0.0
        except Exception as e:
            print(f"Error getting expenses this month: {e}")
            return 0.0
    
    def get_expenses_by_category(self, months=1):
        """Get expenses breakdown by category"""
        try:
            now = datetime.now()
            start_date = (now - timedelta(days=30 * months)).date()
            end_date = now.date()
            
            # This would need the Category model to be imported
            # For now, return sample data
            return [
                {'category': 'Matériel', 'amount': 5000.0, 'percentage': 35.0},
                {'category': 'Salaires', 'amount': 4000.0, 'percentage': 28.0},
                {'category': 'Loyer', 'amount': 3000.0, 'percentage': 21.0},
                {'category': 'Utilities', 'amount': 1500.0, 'percentage': 11.0},
                {'category': 'Autres', 'amount': 700.0, 'percentage': 5.0}
            ]
        except Exception as e:
            print(f"Error getting expenses by category: {e}")
            return []
    
    def get_expenses_by_month(self, months=12):
        """Get expense statistics by month"""
        try:
            results = []
            now = datetime.now()
            
            for i in range(months):
                month_date = now - timedelta(days=30 * i)
                month_start = month_date.replace(day=1).date()
                
                if i == 0:
                    month_end = now.date()
                else:
                    next_month_date = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                    month_end = next_month_date - timedelta(days=1)
                
                total = self.session.query(func.sum(Expense.amount)).filter(
                    and_(Expense.date >= month_start, Expense.date <= month_end)
                ).scalar()
                
                results.append({
                    'month': month_start.strftime('%b %Y'),
                    'expenses': float(total) if total else 0.0
                })
            
            return list(reversed(results))
        except Exception as e:
            print(f"Error getting expenses by month: {e}")
            return []
    
    # ==================== TREATMENT STATISTICS ====================
    
    def get_popular_treatments(self, limit=10):
        """Get most popular treatments"""
        try:
            # Group by treatment description and count
            treatments = self.session.query(
                Visit.treatment_description,
                func.count(Visit.id).label('count')
            ).filter(
                Visit.treatment_description.isnot(None)
            ).group_by(Visit.treatment_description).order_by(
                func.count(Visit.id).desc()
            ).limit(limit).all()
            
            return [{
                'treatment': treatment[0],
                'count': treatment[1]
            } for treatment in treatments]
        except Exception as e:
            print(f"Error getting popular treatments: {e}")
            return []
    
    # ==================== SUMMARY METHODS ====================
    
    def get_dashboard_summary(self):
        """Get complete dashboard summary"""
        try:
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
        except Exception as e:
            print(f"Error getting dashboard summary: {e}")
            return {}
    
    def get_kpi_summary(self):
        """Get key performance indicators"""
        try:
            now = datetime.now()
            last_month = now - timedelta(days=30)
            
            # Current month metrics
            current_revenue = self.get_revenue_this_month()
            current_expenses = self.get_expenses_this_month()
            current_patients = self.get_new_patients_this_month()
            
            # Calculate growth rates (simplified)
            return {
                'revenue': {
                    'current': current_revenue,
                    'growth': 15.2  # Placeholder - calculate actual growth
                },
                'expenses': {
                    'current': current_expenses,
                    'growth': -5.8  # Placeholder
                },
                'patients': {
                    'current': current_patients,
                    'growth': 8.3  # Placeholder
                },
                'profit_margin': {
                    'current': ((current_revenue - current_expenses) / current_revenue * 100) if current_revenue > 0 else 0,
                    'growth': 3.2  # Placeholder
                }
            }
        except Exception as e:
            print(f"Error getting KPI summary: {e}")
            return {}
