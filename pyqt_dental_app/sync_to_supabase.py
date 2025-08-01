import os
import sys
import time
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyqt_dental_app.models.database import Base, Patient, Visit

# --- Supabase Configuration ---
# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Validate that environment variables are set
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# --- SQLite Database Configuration ---
# Determine the SQLite database path
APP_DATA_DIR = os.path.expanduser("~/.dentistedb")
SQLITE_DB_PATH = os.path.join(APP_DATA_DIR, "patients.db")

# SQLAlchemy setup for SQLite
engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Sync Logic ---

def get_last_sync_timestamp(table_name: str) -> datetime:
    """Reads the last successful sync timestamp for a given table."""
    # This could be stored in a local file, a separate SQLite table, or even Supabase itself.
    # For simplicity, we'll use a local file for each table.
    sync_file = os.path.join(APP_DATA_DIR, f'{table_name}_last_sync.txt')
    if os.path.exists(sync_file):
        with open(sync_file, 'r') as f:
            timestamp_str = f.read().strip()
            if timestamp_str:
                return datetime.fromisoformat(timestamp_str)
    return datetime.min # Return a very old date if no sync has occurred

def update_last_sync_timestamp(table_name: str, timestamp: datetime):
    """Updates the last successful sync timestamp for a given table."""
    sync_file = os.path.join(APP_DATA_DIR, f'{table_name}_last_sync.txt')
    with open(sync_file, 'w') as f:
        f.write(timestamp.isoformat())

def serialize_patient(patient: Patient) -> dict:
    """Serializes a Patient object to a dictionary suitable for Supabase."""
    return {
        'id': patient.id,
        'nom': patient.nom, # Corrected from 'name'
        'prenom': patient.prenom, # Added for first name
        'date_naissance': patient.date_naissance.isoformat() if patient.date_naissance else None,
        'telephone': patient.telephone, # Corrected from 'phone'
        'numero_carte_national': patient.numero_carte_national, # Corrected from 'email' or 'address'
        'assurance': patient.assurance, # Corrected from 'gender'
        'profession': patient.profession, # Corrected from 'date_of_birth'
        'maladie': patient.maladie, # Corrected from 'medical_history'
        'observation': patient.observation, # Added for observation
        'xray_photo': patient.xray_photo, # Added for xray_photo
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

def sync_patients(session, supabase):
    last_sync = get_last_sync_timestamp('patients') # Get last sync timestamp for patients
    print(f"[Patients] Last sync: {last_sync}")

    print("Syncing patients...")
    # Fetch new or updated patients
    patients_to_sync = session.query(Patient).filter(Patient.updated_at > last_sync.date()).all()
    print(f"Found {len(patients_to_sync)} patients to sync.")

    if not patients_to_sync:
        return True, last_sync # Nothing to sync

    patients_to_upsert = []  # Initialize patients_to_upsert
    for patient in patients_to_sync:
        patients_to_upsert.append(serialize_patient(patient)) # Use the corrected serialize_patient function
    try:
        supabase.table("patients").upsert(patients_to_upsert).execute()
        print(f"Successfully synced {len(patients_to_upsert)} patients.")
        return True, datetime.now() # Update sync timestamp to now
    except Exception as e:
        print(f"Error syncing patients: {e}")
        return False, last_sync # Keep old timestamp for retry

def sync_visits(session):
    """Syncs visit data from SQLite to Supabase."""
    last_sync = get_last_sync_timestamp('visits')
    print(f"[Visits] Last sync: {last_sync}")

    # Fetch new or updated visits
    visits_to_sync = session.query(Visit).filter(Visit.updated_at > last_sync.date()).all()
    print(f"[Visits] Found {len(visits_to_sync)} visits to sync.")

    if not visits_to_sync:
        return True, last_sync # Nothing to sync

    data_to_upsert = [serialize_visit(v) for v in visits_to_sync]

    try:
        # Use upsert (on_conflict) to insert new records or update existing ones
        response = supabase.from_('visits').upsert(data_to_upsert, on_conflict='id').execute()
        response.data # Access data to trigger potential errors
        print(f"[Visits] Successfully synced {len(data_to_upsert)} visits.")
        return True, datetime.now() # Update sync timestamp to now
    except Exception as e:
        print(f"[Visits] Error syncing visits: {e}")
        return False, last_sync # Keep old timestamp for retry

def run_sync():
    """Main function to run the synchronization process."""
    print("Starting Supabase synchronization...")
    session = SessionLocal()
    try:
        # Sync Patients
        patients_synced, new_patients_sync_time = sync_patients(session, supabase) # Pass supabase here
        if patients_synced:
            update_last_sync_timestamp('patients', new_patients_sync_time)
        
        # Sync Visits
        visits_synced, new_visits_sync_time = sync_visits(session)
        if visits_synced:
            update_last_sync_timestamp('visits', new_visits_sync_time)

        if patients_synced and visits_synced:
            print("Synchronization completed successfully.")
        else:
            print("Synchronization failed for some tables. Will retry later.")

    finally:
        session.close()

if __name__ == "__main__":
    # This script can be run periodically (e.g., via a cron job or a simple loop)
    # For demonstration, we'll run it once.
    # In a real application, you might want a more robust scheduler or a background thread.
    
    # Simple retry loop for demonstration
    MAX_RETRIES = 5
    RETRY_DELAY_SECONDS = 10

    for attempt in range(MAX_RETRIES):
        print(f"Attempt {attempt + 1}/{MAX_RETRIES} to sync...")
        try:
            run_sync()
            break # Exit loop if sync is successful
        except Exception as e:
            print(f"An unexpected error occurred during sync: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Max retries reached. Synchronization failed.")