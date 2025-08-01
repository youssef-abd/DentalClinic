"""
Database models for the PyQt Dental Cabinet Application
Migrated from Flask-SQLAlchemy to pure SQLAlchemy for desktop use
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(Base):
    """Patient model for storing patient information"""
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date)  # Date of birth
    telephone = Column(String(20))
    numero_carte_national = Column(String(50))
    assurance = Column(String(100))
    profession = Column(String(100))
    maladie = Column(String(200))
    observation = Column(Text)
    xray_photo = Column(String(255))  # Store the path to the X-ray photo
    created_at = Column(Date, default=datetime.now().date)
    updated_at = Column(Date, default=datetime.now().date, onupdate=datetime.now().date) # Added for sync
    
    # Relationships
    visits = relationship('Visit', back_populates='patient', cascade='all, delete-orphan')
    tooth_statuses = relationship('ToothStatus', back_populates='patient', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        """Return full name of patient"""
        return f"{self.prenom} {self.nom}".strip()
    
    @property
    def total_unpaid(self):
        """Calculate total unpaid amount across all visits"""
        return sum(visit.reste for visit in self.visits if visit.reste > 0)
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'

class Visit(Base):
    """Visit model for storing patient visit information"""
    __tablename__ = 'visits'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.now().date)
    dent = Column(String(10))  # Tooth number for the treatment
    acte = Column(Text)  # Treatment/procedure performed
    prix = Column(Float, default=0.0)  # Total price
    paye = Column(Float, default=0.0)  # Amount paid
    reste = Column(Float, default=0.0)  # Remaining amount
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    updated_at = Column(Date, default=datetime.now().date, onupdate=datetime.now().date) # Added for sync
    
    # Relationship with patient
    patient = relationship('Patient', back_populates='visits')
    
    def calculate_reste(self):
        """Calculate and update remaining amount"""
        self.reste = (self.prix or 0.0) - (self.paye or 0.0)
    
    def __repr__(self):
        return f'<Visit {self.id} for Patient {self.patient_id}>'

class ToothStatus(Base):
    """Tooth status model for tracking individual tooth conditions"""
    __tablename__ = 'tooth_status'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    tooth_number = Column(Integer, nullable=False)  # 1-32 (adult teeth)
    status = Column(String(50), default='normal')  # normal, carie, couronne, bridge, implant, extraction, etc.
    notes = Column(Text)  # Additional notes about the tooth
    date_recorded = Column(Date, default=datetime.now().date)
    created_at = Column(Date, default=datetime.now().date)
    
    # Relationship with patient
    patient = relationship('Patient', back_populates='tooth_statuses')
    
    def __repr__(self):
        return f'<ToothStatus {self.tooth_number} ({self.status}) for Patient {self.patient_id}>'

class DatabaseManager:
    """Database manager for handling SQLAlchemy operations"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Create app data directory in user's home folder
            app_data_dir = os.path.expanduser("~/.dentistedb")
            os.makedirs(app_data_dir, exist_ok=True)
            db_path = os.path.join(app_data_dir, "patients.db")
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables"""
        # Import inventory models to ensure they are registered with Base
        from .inventory_models import InventoryCategory, InventoryItem, InventoryTransaction, Supplier
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def init_default_user(self):
        """Create default admin user if it doesn't exist"""
        session = self.get_session()
        try:
            admin_user = session.query(User).filter_by(username='mouna').first()
            if not admin_user:
                admin_user = User(username='mouna')
                admin_user.set_password('123')
                session.add(admin_user)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if backup_path is None:
            backup_dir = os.path.expanduser("~/.dentistedb/backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"patients_backup_{timestamp}.db")
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
