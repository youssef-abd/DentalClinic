"""
Expense Management Models for Dental Practice
Handles all expense-related database models and relationships
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ExpenseCategory(Base):
    """Expense categories for organizing expenses"""
    __tablename__ = 'expense_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7), default='#3B82F6')  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    expenses = relationship("Expense", back_populates="category")
    
    def __repr__(self):
        return f"<ExpenseCategory(id={self.id}, name='{self.name}')>"

class ExpenseSupplier(Base):
    """Suppliers/vendors for expenses"""
    __tablename__ = 'expense_suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    tax_id = Column(String(50))  # For tax purposes
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    expenses = relationship("Expense", back_populates="supplier")
    
    def __repr__(self):
        return f"<ExpenseSupplier(id={self.id}, name='{self.name}')>"

class Expense(Base):
    """Main expense records"""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('expense_categories.id'))
    supplier_id = Column(Integer, ForeignKey('expense_suppliers.id'), nullable=True)
    
    # Additional fields
    invoice_number = Column(String(100))
    payment_method = Column(String(50), default='cash')  # cash, check, card, transfer
    is_tax_deductible = Column(Boolean, default=True)
    tax_amount = Column(Float, default=0.0)
    
    # File attachments (store file paths)
    receipt_file = Column(String(500))  # Path to receipt image/PDF
    
    # Status and metadata
    status = Column(String(20), default='pending')  # pending, approved, rejected
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("ExpenseCategory", back_populates="expenses")
    supplier = relationship("ExpenseSupplier", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(id={self.id}, description='{self.description}', amount={self.amount})>"

class ExpenseRecurring(Base):
    """Recurring expenses (rent, utilities, etc.)"""
    __tablename__ = 'expense_recurring'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    
    # Recurrence settings
    frequency = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)  # Optional end date
    next_due_date = Column(DateTime, nullable=False)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('expense_categories.id'))
    supplier_id = Column(Integer, ForeignKey('expense_suppliers.id'), nullable=True)
    
    # Settings
    auto_create = Column(Boolean, default=False)  # Auto-create expense records
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("ExpenseCategory")
    supplier = relationship("ExpenseSupplier")
    
    def __repr__(self):
        return f"<ExpenseRecurring(id={self.id}, name='{self.name}', frequency='{self.frequency}')>"
