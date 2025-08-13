"""
Expense Management Service
Handles all expense-related business logic and database operations
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, func, extract
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
import shutil

from ..models.expense_models import Expense, ExpenseCategory, ExpenseSupplier, ExpenseRecurring
from ..models.database import DatabaseManager

# Initialize database manager and engine globally for the service module
_db_manager = DatabaseManager()
# Ensure all tables (including expense and related) are created once at import time
try:
    # Import here to register models with Base before table creation
    from ..models import expense_models  # noqa: F401
    _db_manager.create_tables()
    # Ensure expense tables exist (expense models use a separate Base)
    expense_models.Base.metadata.create_all(bind=_db_manager.engine)
except Exception:
    # Silently ignore if tables already exist or any other error; it will surface later if critical
    pass

engine = _db_manager.engine
Session = sessionmaker(bind=engine)

class ExpenseService:
    """Service class for expense management operations"""
    
    def __init__(self):
        self.session = Session()
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    # ==================== EXPENSE OPERATIONS ====================
    
    def create_expense(self, date, description, amount, category_id, supplier_id=None,
                      invoice_number=None, payment_method='cash', is_tax_deductible=True,
                      tax_amount=0.0, receipt_file=None, notes=None):
        """Create a new expense record"""
        try:
            print("\n=== DEBUT create_expense ===")
            print(f"Création d'une nouvelle dépense:")
            print(f"  Date: {date} (type: {type(date)})")
            print(f"  Description: {description}")
            print(f"  Montant: {amount}")
            print(f"  Catégorie ID: {category_id}")
            print(f"  Fournisseur ID: {supplier_id}")
            print(f"  N° Facture: {invoice_number}")
            print(f"  Mode de paiement: {payment_method}")
            print(f"  Déductible fiscalement: {is_tax_deductible}")
            print(f"  Montant TVA: {tax_amount}")
            
            expense = Expense(
                date=date,
                description=description,
                amount=float(amount),
                category_id=category_id,
                supplier_id=supplier_id,
                invoice_number=invoice_number,
                payment_method=payment_method,
                is_tax_deductible=is_tax_deductible,
                tax_amount=float(tax_amount) if tax_amount else 0.0,
                receipt_file=receipt_file,
                notes=notes,
                status='approved'  # Default to approved
            )
            
            print("Objet Expense créé, ajout à la session...")
            self.session.add(expense)
            print("Commit de la transaction...")
            self.session.commit()
            print(f"Dépense créée avec succès! ID: {expense.id}")
            print("=== FIN create_expense ===\n")
            return expense.id
            
        except Exception as e:
            print(f"ERREUR lors de la création de la dépense: {str(e)}")
            import traceback
            print("Traceback:", traceback.format_exc())
            self.session.rollback()
            raise Exception(f"Error creating expense: {str(e)}")
    
    def get_expense(self, expense_id):
        """Get expense by ID"""
        return self.session.query(Expense).filter(Expense.id == expense_id).first()
    
    def get_all_expenses(self, limit=None, offset=0):
        """Get all expenses with optional pagination"""
        query = self.session.query(Expense).order_by(Expense.date.desc())
        
        if limit:
            query = query.limit(limit).offset(offset)
            
        return query.all()
    
    def get_expenses_by_date_range(self, start_date, end_date):
        """Get expenses within a date range"""
        print(f"\n=== DEBUT get_expenses_by_date_range ===")
        print(f"Recherche des dépenses entre {start_date} (type: {type(start_date)}) et {end_date} (type: {type(end_date)})")
        
        # Log the query being executed
        query = self.session.query(Expense).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).order_by(Expense.date.desc())
        
        # Log the generated SQL for debugging
        sql = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        print(f"SQL Query: {sql}")
        
        # Execute and log results
        results = query.all()
        print(f"{len(results)} dépenses trouvées dans cette plage")
        
        # Afficher les dates des dépenses trouvées
        if results:
            print("Dépenses trouvées (par date décroissante):")
            for i, expense in enumerate(results, 1):
                print(f"  {i}. {expense.date} - {expense.description} ({expense.amount} MAD)")
        else:
            print("Aucune dépense trouvée dans cette plage de dates.")
            
            # Vérifier s'il y a des dépenses dans la base de données
            all_expenses = self.session.query(Expense).order_by(Expense.date.desc()).all()
            if all_expenses:
                print("\nDépenses existantes dans la base de données (toutes dates):")
                for i, exp in enumerate(all_expenses[:5], 1):  # Afficher les 5 premières dépenses
                    print(f"  {i}. {exp.date} - {exp.description} ({exp.amount} MAD)")
                if len(all_expenses) > 5:
                    print(f"  ... et {len(all_expenses) - 5} autres dépenses")
            else:
                print("Aucune dépense trouvée dans la base de données.")
                
        print("=== FIN get_expenses_by_date_range ===\n")
            
        return results
    
    def get_expenses_by_category(self, category_id):
        """Get expenses by category"""
        return self.session.query(Expense).filter(
            Expense.category_id == category_id
        ).order_by(Expense.date.desc()).all()
    
    def get_expenses_by_supplier(self, supplier_id):
        """Get expenses by supplier"""
        return self.session.query(Expense).filter(
            Expense.supplier_id == supplier_id
        ).order_by(Expense.date.desc()).all()
    
    def update_expense(self, expense_id, **kwargs):
        """Update expense record"""
        try:
            expense = self.get_expense(expense_id)
            if not expense:
                raise Exception("Expense not found")
            
            for key, value in kwargs.items():
                if hasattr(expense, key):
                    setattr(expense, key, value)
            
            expense.updated_at = datetime.utcnow()
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error updating expense: {str(e)}")
    
    def delete_expense(self, expense_id):
        """Delete expense record"""
        try:
            expense = self.get_expense(expense_id)
            if not expense:
                raise Exception("Expense not found")
            
            # Delete associated receipt file if exists
            if expense.receipt_file and os.path.exists(expense.receipt_file):
                os.remove(expense.receipt_file)
            
            self.session.delete(expense)
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error deleting expense: {str(e)}")
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def create_category(self, name, description=None, color='#3B82F6'):
        """Create a new expense category"""
        try:
            category = ExpenseCategory(
                name=name,
                description=description,
                color=color
            )
            
            self.session.add(category)
            self.session.commit()
            return category.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error creating category: {str(e)}")
    
    def get_all_categories(self, active_only=True):
        """Get all expense categories"""
        query = self.session.query(ExpenseCategory)
        
        if active_only:
            query = query.filter(ExpenseCategory.is_active == True)
            
        return query.order_by(ExpenseCategory.name).all()
    
    def get_category(self, category_id):
        """Get category by ID"""
        return self.session.query(ExpenseCategory).filter(
            ExpenseCategory.id == category_id
        ).first()
    
    def update_category(self, category_id, **kwargs):
        """Update category"""
        try:
            category = self.get_category(category_id)
            if not category:
                raise Exception("Category not found")
            
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error updating category: {str(e)}")
    
    def delete_category(self, category_id):
        """Delete category by reassigning related records to a default category."""
        try:
            category = self.get_category(category_id)
            if not category:
                raise Exception("Category not found")

            # Find or create default category
            default_name = "Sans catégorie"
            default_category = self.session.query(ExpenseCategory).filter(ExpenseCategory.name == default_name).first()
            if not default_category:
                default_category = ExpenseCategory(name=default_name, description="Catégorie par défaut", color="#9E9E9E")
                self.session.add(default_category)
                self.session.flush()  # assign id

            # Reassign expenses
            self.session.query(Expense).filter(Expense.category_id == category_id).update(
                {Expense.category_id: default_category.id}, synchronize_session=False
            )

            # Reassign recurring expenses
            self.session.query(ExpenseRecurring).filter(ExpenseRecurring.category_id == category_id).update(
                {ExpenseRecurring.category_id: default_category.id}, synchronize_session=False
            )

            self.session.flush()
            self.session.delete(category)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error deleting category: {str(e)}")
    
    # ==================== SUPPLIER OPERATIONS ====================
    
    def create_supplier(self, name, contact_person=None, phone=None, email=None,
                       address=None, tax_id=None, notes=None):
        """Create a new supplier"""
        try:
            supplier = ExpenseSupplier(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                tax_id=tax_id,
                notes=notes
            )
            
            self.session.add(supplier)
            self.session.commit()
            return supplier.id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error creating supplier: {str(e)}")
    
    def get_all_suppliers(self, active_only=True):
        """Get all suppliers"""
        query = self.session.query(ExpenseSupplier)
        
        if active_only:
            query = query.filter(ExpenseSupplier.is_active == True)
            
        return query.order_by(ExpenseSupplier.name).all()
    
    def get_supplier(self, supplier_id):
        """Get supplier by ID"""
        return self.session.query(ExpenseSupplier).filter(
            ExpenseSupplier.id == supplier_id
        ).first()
    
    def update_supplier(self, supplier_id, **kwargs):
        """Update supplier"""
        try:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                raise Exception("Supplier not found")
            
            for key, value in kwargs.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error updating supplier: {str(e)}")
    
    def delete_supplier(self, supplier_id):
        """Delete supplier (only if no expenses are associated)"""
        try:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                raise Exception("Supplier not found")
            
            # Check if supplier has expenses
            expense_count = self.session.query(Expense).filter(
                Expense.supplier_id == supplier_id
            ).count()
            
            if expense_count > 0:
                raise Exception(f"Cannot delete supplier. {expense_count} expenses are associated with it.")
            
            self.session.delete(supplier)
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error deleting supplier: {str(e)}")
    
    # ==================== ANALYTICS AND REPORTS ====================
    
    def get_monthly_expenses(self, year, month):
        """Get total expenses for a specific month"""
        return self.session.query(func.sum(Expense.amount)).filter(
            and_(
                extract('year', Expense.date) == year,
                extract('month', Expense.date) == month
            )
        ).scalar() or 0.0
    
    def get_yearly_expenses(self, year):
        """Get total expenses for a specific year"""
        return self.session.query(func.sum(Expense.amount)).filter(
            extract('year', Expense.date) == year
        ).scalar() or 0.0
    
    def get_expenses_by_category_summary(self, start_date=None, end_date=None):
        """Get expense summary grouped by category"""
        query = self.session.query(
            ExpenseCategory.name,
            ExpenseCategory.color,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(Expense).group_by(ExpenseCategory.id, ExpenseCategory.name, ExpenseCategory.color)
        
        if start_date and end_date:
            query = query.filter(and_(Expense.date >= start_date, Expense.date <= end_date))
        
        return query.all()
    
    def get_monthly_trend(self, months=12):
        """Get monthly expense trend for the last N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        return self.session.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).filter(
            Expense.date >= start_date
        ).group_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).order_by(
            extract('year', Expense.date),
            extract('month', Expense.date)
        ).all()
    
    def get_top_suppliers(self, limit=10, start_date=None, end_date=None):
        """Get top suppliers by expense amount"""
        query = self.session.query(
            ExpenseSupplier.name,
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).join(Expense).group_by(ExpenseSupplier.id, ExpenseSupplier.name)
        
        if start_date and end_date:
            query = query.filter(and_(Expense.date >= start_date, Expense.date <= end_date))
        
        return query.order_by(func.sum(Expense.amount).desc()).limit(limit).all()
    
    # ==================== FILE MANAGEMENT ====================
    
    def save_receipt_file(self, expense_id, file_path):
        """Save receipt file for an expense"""
        try:
            # Create receipts directory if it doesn't exist
            receipts_dir = os.path.join(os.path.dirname(__file__), '..', 'receipts')
            os.makedirs(receipts_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file_path)[1]
            new_filename = f"receipt_{expense_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            new_file_path = os.path.join(receipts_dir, new_filename)
            
            # Copy file to receipts directory
            shutil.copy2(file_path, new_file_path)
            
            # Update expense record
            self.update_expense(expense_id, receipt_file=new_file_path)
            
            return new_file_path
            
        except Exception as e:
            raise Exception(f"Error saving receipt file: {str(e)}")
    
    # ==================== SEARCH AND FILTER ====================
    
    def search_expenses(self, search_term, start_date=None, end_date=None, 
                       category_id=None, supplier_id=None):
        """Search expenses with multiple filters"""
        query = self.session.query(Expense)
        
        # Text search in description and invoice number
        if search_term:
            query = query.filter(
                or_(
                    Expense.description.contains(search_term),
                    Expense.invoice_number.contains(search_term),
                    Expense.notes.contains(search_term)
                )
            )
        
        # Date range filter
        if start_date and end_date:
            query = query.filter(and_(Expense.date >= start_date, Expense.date <= end_date))
        
        # Category filter
        if category_id:
            query = query.filter(Expense.category_id == category_id)
        
        # Supplier filter
        if supplier_id:
            query = query.filter(Expense.supplier_id == supplier_id)
        
        return query.order_by(Expense.date.desc()).all()
