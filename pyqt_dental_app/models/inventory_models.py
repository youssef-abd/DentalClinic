"""
Inventory models for the PyQt Dental Cabinet Application
Models for managing dental supplies and equipment inventory
"""

from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class InventoryCategory(Base):
    """Category model for organizing inventory items"""
    __tablename__ = 'inventory_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(Date, default=datetime.now().date)
    
    # Relationships
    items = relationship('InventoryItem', back_populates='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<InventoryCategory {self.name}>'

class InventoryItem(Base):
    """Inventory item model for dental supplies and equipment"""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    reference = Column(String(100))  # Product reference/SKU
    brand = Column(String(100))
    supplier = Column(String(200))
    
    # Stock information
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=0)  # Alert threshold
    maximum_stock = Column(Integer, default=100)
    unit = Column(String(50), default='pièce')  # unit, box, ml, etc.
    
    # Pricing
    unit_cost = Column(Float, default=0.0)  # Cost per unit
    selling_price = Column(Float, default=0.0)  # Selling price per unit
    
    # Status and tracking
    is_active = Column(Boolean, default=True)
    expiry_date = Column(Date)
    location = Column(String(100))  # Storage location
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('inventory_categories.id'))
    
    # Relationships
    category = relationship('InventoryCategory', back_populates='items')
    transactions = relationship('InventoryTransaction', back_populates='item', cascade='all, delete-orphan')
    
    # Timestamps
    created_at = Column(Date, default=datetime.now().date)
    updated_at = Column(Date, default=datetime.now().date)
    
    @property
    def is_low_stock(self):
        """Check if item is below minimum stock threshold"""
        return self.current_stock <= self.minimum_stock
    
    @property
    def is_expired(self):
        """Check if item is expired"""
        if self.expiry_date:
            return self.expiry_date < datetime.now().date()
        return False
    
    @property
    def stock_value(self):
        """Calculate total value of current stock"""
        return self.current_stock * self.unit_cost
    
    def __repr__(self):
        return f'<InventoryItem {self.name} ({self.current_stock} {self.unit})>'

class InventoryTransaction(Base):
    """Transaction model for tracking inventory movements"""
    __tablename__ = 'inventory_transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_type = Column(String(20), nullable=False)  # 'in', 'out', 'adjustment'
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Transaction details
    reason = Column(String(200))  # Purchase, sale, usage, waste, etc.
    reference_number = Column(String(100))  # Invoice number, order number, etc.
    notes = Column(Text)
    
    # Stock levels after transaction
    stock_before = Column(Integer, default=0)
    stock_after = Column(Integer, default=0)
    
    # Foreign keys
    item_id = Column(Integer, ForeignKey('inventory_items.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    item = relationship('InventoryItem', back_populates='transactions')
    
    # Timestamps
    transaction_date = Column(Date, default=datetime.now().date)
    created_at = Column(Date, default=datetime.now().date)
    
    def __repr__(self):
        return f'<InventoryTransaction {self.transaction_type} {self.quantity} of {self.item.name if self.item else "Unknown"}>'

class Supplier(Base):
    """Supplier model for managing vendor information"""
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    
    # Business details
    tax_id = Column(String(50))
    payment_terms = Column(String(100))  # Net 30, etc.
    notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(Date, default=datetime.now().date)
    updated_at = Column(Date, default=datetime.now().date)
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
