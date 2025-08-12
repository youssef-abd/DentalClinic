# modified_sync.py - Updated version of your original sync code
import os
import sys
import time
import logging
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from supabase import create_client, Client
from dotenv import load_dotenv

# Set up logging instead of print statements
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyqt_dental_app.models.database import Base, Patient, Visit

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- SQLite Database Configuration ---
APP_DATA_DIR = os.path.expanduser("~/.dentistedb")
SQLITE_DB_PATH = os.path.join(APP_DATA_DIR, "patients.db")

engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Modified Sync Logic ---

def get_last_sync_timestamp(table_name: str) -> datetime:
    """Reads the last successful sync timestamp for a given table."""
    sync_file = os.path.join(APP_DATA_DIR, f'{table_name}_last_sync.txt')
    if os.path.exists(sync_file):
        with open(sync_file, 'r') as f:
            timestamp_str = f.read().strip()
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
    return datetime.min

def update_last_sync_timestamp(table_name: str, timestamp: datetime):
    """Updates the last successful sync timestamp for a given table."""
    sync_file = os.path.join(APP_DATA_DIR, f'{table_name}_last_sync.txt')
    with open(sync_file, 'w') as f:
        f.write(timestamp.isoformat())

def serialize_patient(patient: Patient) -> dict:
    """Serializes a Patient object to a dictionary suitable for Supabase."""
    return {
        'id': patient.id,
        'nom': patient.nom,
        'prenom': patient.prenom,
        'date_naissance': patient.date_naissance.isoformat() if patient.date_naissance else None,
        'telephone': patient.telephone,
        'numero_carte_national': patient.numero_carte_national,
        'assurance': patient.assurance,
        'profession': patient.profession,
        'maladie': patient.maladie,
        'observation': patient.observation,
        'xray_photo': patient.xray_photo,
        'created_at': patient.created_at.isoformat() if patient.created_at else None,
        'updated_at': patient.updated_at.isoformat() if patient.updated_at else None,
    }

def serialize_visit(visit: Visit) -> dict:
    """Serializes a Visit object to a dictionary suitable for Supabase."""
    return {
        'id': visit.id,
        'date': visit.date.isoformat() if visit.date else None,
        'dent': visit.dent,
        'acte': visit.acte,
        'prix': float(visit.prix),
        'paye': float(visit.paye),
        'reste': float(visit.reste),
        'patient_id': visit.patient_id,
        'updated_at': visit.updated_at.isoformat() if visit.updated_at else None,
    }

def sync_patients(session, supabase, silent=False):
    """
    Syncs patient data from SQLite to Supabase.
    Returns (success: bool, records_synced: int, new_timestamp: datetime)
    """
    last_sync = get_last_sync_timestamp('patients')
    
    # Query patients to sync
    patients_to_sync = session.query(Patient).filter(Patient.updated_at > last_sync.date()).all()
    records_count = len(patients_to_sync)
    
    if not silent:
        logger.info(f"[Patients] Found {records_count} patients to sync since {last_sync}")
    
    if not patients_to_sync:
        return True, 0, last_sync  # Nothing to sync

    # Serialize patients
    patients_to_upsert = [serialize_patient(patient) for patient in patients_to_sync]
    
    try:
        supabase.table("patients").upsert(patients_to_upsert).execute()
        new_timestamp = datetime.now()
        
        if not silent:
            logger.info(f"[Patients] Successfully synced {records_count} patients.")
        
        return True, records_count, new_timestamp
        
    except Exception as e:
        if not silent:
            logger.error(f"[Patients] Error syncing: {e}")
        return False, 0, last_sync

def sync_visits(session, supabase, silent=False):
    """
    Syncs visit data from SQLite to Supabase.
    Returns (success: bool, records_synced: int, new_timestamp: datetime)
    """
    last_sync = get_last_sync_timestamp('visits')
    
    # Query visits to sync
    visits_to_sync = session.query(Visit).filter(Visit.updated_at > last_sync.date()).all()
    records_count = len(visits_to_sync)
    
    if not silent:
        logger.info(f"[Visits] Found {records_count} visits to sync since {last_sync}")

    if not visits_to_sync:
        return True, 0, last_sync  # Nothing to sync

    data_to_upsert = [serialize_visit(v) for v in visits_to_sync]

    try:
        response = supabase.from_('visits').upsert(data_to_upsert, on_conflict='id').execute()
        response.data  # Access data to trigger potential errors
        new_timestamp = datetime.now()
        
        if not silent:
            logger.info(f"[Visits] Successfully synced {records_count} visits.")
            
        return True, records_count, new_timestamp
        
    except Exception as e:
        if not silent:
            logger.error(f"[Visits] Error syncing: {e}")
        return False, 0, last_sync

def run_sync(silent=False):
    """
    Main function to run the synchronization process.
    Returns (success: bool, patients_synced: int, visits_synced: int)
    """
    if not silent:
        logger.info("Starting Supabase synchronization...")
    
    session = SessionLocal()
    total_patients = 0
    total_visits = 0
    overall_success = True
    
    try:
        # Sync Patients
        patients_success, patients_count, patients_timestamp = sync_patients(session, supabase, silent)
        if patients_success:
            update_last_sync_timestamp('patients', patients_timestamp)
            total_patients = patients_count
        else:
            overall_success = False
        
        # Sync Visits
        visits_success, visits_count, visits_timestamp = sync_visits(session, silent)
        if visits_success:
            update_last_sync_timestamp('visits', visits_timestamp)
            total_visits = visits_count
        else:
            overall_success = False

        if not silent:
            if overall_success:
                logger.info(f"Synchronization completed successfully. Patients: {total_patients}, Visits: {total_visits}")
            else:
                logger.warning("Synchronization failed for some tables.")
                
        return overall_success, total_patients, total_visits

    except Exception as e:
        if not silent:
            logger.error(f"Unexpected error during sync: {e}")
        return False, 0, 0
    finally:
        session.close()

def get_sync_statistics():
    """Get sync statistics for UI display"""
    try:
        session = SessionLocal()
        
        # Get last sync times
        patients_last_sync = get_last_sync_timestamp('patients')
        visits_last_sync = get_last_sync_timestamp('visits')
        
        # Count pending records
        pending_patients = session.query(Patient).filter(Patient.updated_at > patients_last_sync.date()).count()
        pending_visits = session.query(Visit).filter(Visit.updated_at > visits_last_sync.date()).count()
        
        # Total counts
        total_patients = session.query(Patient).count()
        total_visits = session.query(Visit).count()
        
        return {
            'patients': {
                'last_sync': patients_last_sync.isoformat() if patients_last_sync != datetime.min else None,
                'pending': pending_patients,
                'total': total_patients
            },
            'visits': {
                'last_sync': visits_last_sync.isoformat() if visits_last_sync != datetime.min else None,
                'pending': pending_visits,
                'total': total_visits
            }
        }
    except Exception as e:
        logger.error(f"Error getting sync statistics: {e}")
        return None
    finally:
        session.close()

# Legacy support - keep original function for backward compatibility
def run_sync_legacy():
    """Original sync function for backward compatibility"""
    success, patients, visits = run_sync(silent=False)
    return success

if __name__ == "__main__":
    # For manual testing only
    success, patients_synced, visits_synced = run_sync(silent=False)
    if success:
        print(f"Sync completed: {patients_synced} patients, {visits_synced} visits")
    else:
        print("Sync failed")