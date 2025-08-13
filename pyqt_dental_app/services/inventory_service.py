"""
Inventory Service for managing dental supplies and equipment
Handles all inventory-related operations including stock management, transactions, and reporting
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime, date, timedelta
from ..models.database import DatabaseManager
from ..models.inventory_models import InventoryItem, InventoryCategory, InventoryTransaction, Supplier

class InventoryService:
    """Service class for inventory management operations"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    # Category Management
    def create_category(self, name, description=""):
        """Create a new inventory category"""
        session = self.db_manager.get_session()
        try:
            category = InventoryCategory(
                name=name,
                description=description
            )
            session.add(category)
            session.commit()
            return category.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_categories(self):
        """Get all inventory categories"""
        session = self.db_manager.get_session()
        try:
            categories = session.query(InventoryCategory).order_by(InventoryCategory.name).all()
            return [(cat.id, cat.name, cat.description) for cat in categories]
        finally:
            session.close()
    
    def delete_category(self, category_id):
        """Delete a category. If items exist, reassign them to a default category."""
        session = self.db_manager.get_session()
        try:
            category = session.query(InventoryCategory).filter_by(id=category_id).first()
            if not category:
                return False
            
            # Prevent deleting the default category
            default_name = "Sans catégorie"
            if category.name == default_name:
                return False
            
            # Ensure a default category exists to avoid delete-orphan on items
            default_category = session.query(InventoryCategory).filter(InventoryCategory.name == default_name).first()
            if not default_category:
                default_category = InventoryCategory(name=default_name, description="Catégorie par défaut")
                session.add(default_category)
                session.flush()  # get id
            
            # Reassign items to default category using ORM updates to avoid delete-orphan issues
            items = session.query(InventoryItem).filter(InventoryItem.category_id == category.id).all()
            for it in items:
                it.category_id = default_category.id
            session.flush()
            
            # Now safe to delete the category
            session.delete(category)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Item Management
    def create_item(self, name, description="", reference="", brand="", supplier="",
                   current_stock=0, minimum_stock=0, maximum_stock=100, unit="pièce",
                   unit_cost=0.0, selling_price=0.0, category_id=None, expiry_date=None, location="", is_active=True):
        """Create a new inventory item"""
        session = self.db_manager.get_session()
        try:
            item = InventoryItem(
                name=name,
                description=description,
                reference=reference,
                brand=brand,
                supplier=supplier,
                current_stock=current_stock,
                minimum_stock=minimum_stock,
                maximum_stock=maximum_stock,
                unit=unit,
                unit_cost=unit_cost,
                selling_price=selling_price,
                category_id=category_id,
                expiry_date=expiry_date,
                location=location,
                is_active=is_active
            )
            session.add(item)
            session.commit()
            return item.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_items(self, include_inactive=False):
        """Get all inventory items"""
        session = self.db_manager.get_session()
        try:
            query = session.query(InventoryItem)
            if not include_inactive:
                query = query.filter(InventoryItem.is_active == True)
            
            items = query.order_by(InventoryItem.name).all()
            
            result = []
            for item in items:
                result.append({
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'reference': item.reference,
                    'brand': item.brand,
                    'supplier': item.supplier,
                    'current_stock': item.current_stock,
                    'minimum_stock': item.minimum_stock,
                    'maximum_stock': item.maximum_stock,
                    'unit': item.unit,
                    'unit_cost': item.unit_cost,
                    'selling_price': item.selling_price,
                    'category': item.category.name if item.category else "",
                    'category_id': item.category_id,
                    'expiry_date': item.expiry_date,
                    'location': item.location,
                    'is_active': item.is_active,
                    'is_low_stock': item.is_low_stock,
                    'is_expired': item.is_expired,
                    'stock_value': item.stock_value
                })
            return result
        finally:
            session.close()
    
    def get_item_by_id(self, item_id):
        """Get a specific inventory item by ID"""
        session = self.db_manager.get_session()
        try:
            item = session.query(InventoryItem).filter_by(id=item_id).first()
            if item:
                return {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'reference': item.reference,
                    'brand': item.brand,
                    'supplier': item.supplier,
                    'current_stock': item.current_stock,
                    'minimum_stock': item.minimum_stock,
                    'maximum_stock': item.maximum_stock,
                    'unit': item.unit,
                    'unit_cost': item.unit_cost,
                    'selling_price': item.selling_price,
                    'category': item.category.name if item.category else "",
                    'category_id': item.category_id,
                    'expiry_date': item.expiry_date,
                    'location': item.location,
                    'is_active': item.is_active,
                    'is_low_stock': item.is_low_stock,
                    'is_expired': item.is_expired,
                    'stock_value': item.stock_value
                }
            return None
        finally:
            session.close()
    
    def update_item(self, item_id, **kwargs):
        """Update an inventory item"""
        session = self.db_manager.get_session()
        try:
            item = session.query(InventoryItem).filter_by(id=item_id).first()
            if item:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                item.updated_at = datetime.now().date()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_item(self, item_id):
        """Soft delete an inventory item"""
        return self.update_item(item_id, is_active=False)
    
    # Stock Management
    def add_stock(self, item_id, quantity, unit_cost=0.0, reason="Achat", reference_number="", notes="", user_id=None):
        """Add stock to an item"""
        return self._create_transaction(
            item_id, 'in', quantity, unit_cost, reason, reference_number, notes, user_id
        )
    
    def remove_stock(self, item_id, quantity, reason="Utilisation", reference_number="", notes="", user_id=None):
        """Remove stock from an item"""
        return self._create_transaction(
            item_id, 'out', quantity, 0.0, reason, reference_number, notes, user_id
        )
    
    def adjust_stock(self, item_id, new_quantity, reason="Ajustement", notes="", user_id=None):
        """Adjust stock to a specific quantity"""
        session = self.db_manager.get_session()
        try:
            item = session.query(InventoryItem).filter_by(id=item_id).first()
            if not item:
                return False
            
            current_stock = item.current_stock
            difference = new_quantity - current_stock
            
            if difference != 0:
                transaction_type = 'in' if difference > 0 else 'out'
                quantity = abs(difference)
                
                return self._create_transaction(
                    item_id, transaction_type, quantity, 0.0, reason, "", notes, user_id
                )
            return True
        finally:
            session.close()
    
    def _create_transaction(self, item_id, transaction_type, quantity, unit_cost, reason, reference_number, notes, user_id):
        """Create an inventory transaction and update stock"""
        session = self.db_manager.get_session()
        try:
            item = session.query(InventoryItem).filter_by(id=item_id).first()
            if not item:
                return False
            
            stock_before = item.current_stock
            
            # Calculate new stock
            if transaction_type == 'in':
                new_stock = stock_before + quantity
            elif transaction_type == 'out':
                new_stock = max(0, stock_before - quantity)  # Prevent negative stock
            else:  # adjustment
                new_stock = quantity
            
            # Create transaction record
            transaction = InventoryTransaction(
                item_id=item_id,
                transaction_type=transaction_type,
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=quantity * unit_cost,
                reason=reason,
                reference_number=reference_number,
                notes=notes,
                stock_before=stock_before,
                stock_after=new_stock,
                user_id=user_id
            )
            
            # Update item stock
            item.current_stock = new_stock
            item.updated_at = datetime.now().date()
            
            session.add(transaction)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Reporting and Analytics
    def get_low_stock_items(self):
        """Get items that are below minimum stock threshold"""
        session = self.db_manager.get_session()
        try:
            items = session.query(InventoryItem).filter(
                and_(
                    InventoryItem.current_stock <= InventoryItem.minimum_stock,
                    InventoryItem.is_active == True
                )
            ).order_by(InventoryItem.name).all()
            
            return [{
                'id': item.id,
                'name': item.name,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'unit': item.unit,
                'supplier': item.supplier
            } for item in items]
        finally:
            session.close()
    
    def get_expired_items(self):
        """Get items that are expired or expiring soon"""
        session = self.db_manager.get_session()
        try:
            today = datetime.now().date()
            warning_date = today + timedelta(days=30)  # 30 days warning
            
            items = session.query(InventoryItem).filter(
                and_(
                    InventoryItem.expiry_date <= warning_date,
                    InventoryItem.expiry_date.isnot(None),
                    InventoryItem.is_active == True
                )
            ).order_by(InventoryItem.expiry_date).all()
            
            return [{
                'id': item.id,
                'name': item.name,
                'expiry_date': item.expiry_date,
                'current_stock': item.current_stock,
                'unit': item.unit,
                'is_expired': item.expiry_date < today,
                'days_to_expiry': (item.expiry_date - today).days
            } for item in items]
        finally:
            session.close()
    
    def get_inventory_value(self):
        """Calculate total inventory value"""
        session = self.db_manager.get_session()
        try:
            items = session.query(InventoryItem).filter(InventoryItem.is_active == True).all()
            total_value = sum(item.stock_value for item in items)
            return total_value
        finally:
            session.close()
    
    def get_transaction_history(self, item_id=None, limit=100):
        """Get transaction history"""
        session = self.db_manager.get_session()
        try:
            query = session.query(InventoryTransaction)
            
            if item_id:
                query = query.filter(InventoryTransaction.item_id == item_id)
            
            transactions = query.order_by(desc(InventoryTransaction.transaction_date)).limit(limit).all()
            
            return [{
                'id': trans.id,
                'item_name': trans.item.name if trans.item else "Unknown",
                'transaction_type': trans.transaction_type,
                'quantity': trans.quantity,
                'unit_cost': trans.unit_cost,
                'total_cost': trans.total_cost,
                'reason': trans.reason,
                'reference_number': trans.reference_number,
                'stock_before': trans.stock_before,
                'stock_after': trans.stock_after,
                'transaction_date': trans.transaction_date,
                'notes': trans.notes
            } for trans in transactions]
        finally:
            session.close()
    
    def search_items(self, search_term):
        """Search items by name, description, reference, or brand"""
        session = self.db_manager.get_session()
        try:
            search_pattern = f"%{search_term}%"
            items = session.query(InventoryItem).filter(
                and_(
                    or_(
                        InventoryItem.name.ilike(search_pattern),
                        InventoryItem.description.ilike(search_pattern),
                        InventoryItem.reference.ilike(search_pattern),
                        InventoryItem.brand.ilike(search_pattern)
                    ),
                    InventoryItem.is_active == True
                )
            ).order_by(InventoryItem.name).all()
            
            return [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'reference': item.reference,
                'brand': item.brand,
                'current_stock': item.current_stock,
                'unit': item.unit,
                'unit_cost': item.unit_cost,
                'selling_price': item.selling_price,
                'category': item.category.name if item.category else ""
            } for item in items]
        finally:
            session.close()
    
    def init_default_data(self):
        """Initialize default categories and sample items"""
        session = self.db_manager.get_session()
        try:
            # Check if categories already exist
            existing_categories = session.query(InventoryCategory).count()
            if existing_categories > 0:
                return False
            
            # Create default categories
            categories = [
                ("Matériaux de Restauration", "Composites, amalgames, ciments"),
                ("Instruments Dentaires", "Miroirs, sondes, excavateurs"),
                ("Anesthésiques", "Lidocaïne, articaïne"),
                ("Matériaux d'Empreinte", "Alginates, silicones"),
                ("Produits d'Hygiène", "Désinfectants, gants"),
                ("Radiologie", "Films, révélateurs"),
                ("Endodontie", "Limes, obturateurs"),
                ("Parodontologie", "Curettes, détartreurs")
            ]
            
            category_objects = []
            for name, description in categories:
                category = InventoryCategory(name=name, description=description)
                session.add(category)
                category_objects.append(category)
            
            session.commit()
            
            # Create sample items
            sample_items = [
                {
                    'name': 'Composite Universel A2',
                    'description': 'Composite de restauration teinte A2',
                    'reference': 'COMP-A2-001',
                    'brand': 'DentMat',
                    'supplier': 'Dental Supply Co.',
                    'current_stock': 15,
                    'minimum_stock': 5,
                    'unit': 'seringue',
                    'unit_cost': 45.0,
                    'selling_price': 65.0,
                    'category_id': category_objects[0].id,
                    'location': 'Armoire A - Étagère 2'
                },
                {
                    'name': 'Gants Nitrile Taille M',
                    'description': 'Gants d\'examen en nitrile sans poudre',
                    'reference': 'GLV-NIT-M',
                    'brand': 'MedGlove',
                    'supplier': 'Medical Supplies Inc.',
                    'current_stock': 8,
                    'minimum_stock': 10,
                    'unit': 'boîte',
                    'unit_cost': 12.0,
                    'selling_price': 18.0,
                    'category_id': category_objects[4].id,
                    'location': 'Stock Principal'
                },
                {
                    'name': 'Lidocaïne 2% avec Épinéphrine',
                    'description': 'Anesthésique local pour injections',
                    'reference': 'LIDO-2-EPI',
                    'brand': 'AnesthCare',
                    'supplier': 'Pharma Dental',
                    'current_stock': 25,
                    'minimum_stock': 15,
                    'unit': 'cartouche',
                    'unit_cost': 2.5,
                    'selling_price': 4.0,
                    'category_id': category_objects[2].id,
                    'location': 'Réfrigérateur'
                }
            ]
            
            for item_data in sample_items:
                item = InventoryItem(**item_data)
                session.add(item)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
