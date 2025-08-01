"""
Database initialization script for PyQt Dental Cabinet Application
Standalone script for database setup and migrations
"""

import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyqt_dental_app.models.database import DatabaseManager, User, Patient, Visit

def init_database(db_path=None, reset=False):
    """Initialize database with tables and default data"""
    print("🏥 Initialisation de la base de données DentisteDB...")
    
    try:
        # Create database manager
        db_manager = DatabaseManager(db_path)
        
        if reset:
            print("⚠️  Mode reset activé - suppression des données existantes...")
            # In SQLite, we can't easily drop tables, so we'll recreate the database
            if os.path.exists(db_manager.db_path):
                backup_path = f"{db_manager.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(db_manager.db_path, backup_path)
                print(f"📦 Sauvegarde créée: {backup_path}")
        
        # Create tables
        print("\n🔧 Initialisation de la base de données...")
        db_manager.create_tables()
        print("✅ Tables créées avec succès (patients, visits, users, tooth_status)")
        
        # Create default admin user
        print("👤 Création de l'utilisateur administrateur...")
        created = db_manager.init_default_user()
        if created:
            print("✅ Utilisateur administrateur créé (mouna/123)")
        else:
            print("ℹ️  Utilisateur administrateur existe déjà")
        
        # Create directories for file storage
        app_data_dir = os.path.expanduser("~/.dentistedb")
        xray_dir = os.path.join(app_data_dir, "xrays")
        backup_dir = os.path.join(app_data_dir, "backups")
        
        for directory in [app_data_dir, xray_dir, backup_dir]:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Répertoire créé: {directory}")
        
        print(f"🎉 Base de données initialisée avec succès!")
        print(f"📍 Emplacement: {db_manager.db_path}")
        print(f"📁 Données d'application: {app_data_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {str(e)}")
        return False

def create_sample_data(db_path=None):
    """Create sample data for testing"""
    print("🧪 Création de données d'exemple...")
    
    try:
        db_manager = DatabaseManager(db_path)
        session = db_manager.get_session()
        
        # Sample patients
        sample_patients = [
            {
                'nom': 'Benali',
                'prenom': 'Ahmed',
                'telephone': '0661234567',
                'numero_carte_national': 'AB123456',
                'assurance': 'CNSS',
                'profession': 'Ingénieur',
                'maladie': 'Diabète',
                'observation': 'Patient régulier, très coopératif'
            },
            {
                'nom': 'Alami',
                'prenom': 'Fatima',
                'telephone': '0667891234',
                'numero_carte_national': 'CD789012',
                'assurance': 'CNOPS',
                'profession': 'Professeur',
                'maladie': '',
                'observation': 'Première visite'
            },
            {
                'nom': 'Tazi',
                'prenom': 'Mohamed',
                'telephone': '0665555555',
                'numero_carte_national': 'EF345678',
                'assurance': 'Assurance privée',
                'profession': 'Commerçant',
                'maladie': 'Hypertension',
                'observation': 'Sensible aux anesthésiques'
            }
        ]
        
        created_patients = []
        for patient_data in sample_patients:
            patient = Patient(**patient_data)
            session.add(patient)
            session.flush()  # Get the ID
            created_patients.append(patient)
            print(f"👤 Patient créé: {patient.full_name}")
        
        # Sample visits
        from datetime import date, timedelta
        
        sample_visits = [
            # Visits for Ahmed Benali
            {
                'patient_id': created_patients[0].id,
                'date': date.today() - timedelta(days=30),
                'acte': 'Consultation et nettoyage',
                'prix': 200.0,
                'paye': 200.0,
                'reste': 0.0
            },
            {
                'patient_id': created_patients[0].id,
                'date': date.today() - timedelta(days=15),
                'acte': 'Plombage molaire droite',
                'prix': 350.0,
                'paye': 200.0,
                'reste': 150.0
            },
            # Visits for Fatima Alami
            {
                'patient_id': created_patients[1].id,
                'date': date.today() - timedelta(days=7),
                'acte': 'Première consultation et radiographie',
                'prix': 150.0,
                'paye': 0.0,
                'reste': 150.0
            },
            # Visits for Mohamed Tazi
            {
                'patient_id': created_patients[2].id,
                'date': date.today() - timedelta(days=45),
                'acte': 'Extraction dent de sagesse',
                'prix': 400.0,
                'paye': 400.0,
                'reste': 0.0
            },
            {
                'patient_id': created_patients[2].id,
                'date': date.today() - timedelta(days=5),
                'acte': 'Contrôle post-extraction',
                'prix': 100.0,
                'paye': 50.0,
                'reste': 50.0
            }
        ]
        
        for visit_data in sample_visits:
            visit = Visit(**visit_data)
            session.add(visit)
            print(f"📅 Visite créée: {visit_data['acte']} - {visit_data['prix']} DH")
        
        session.commit()
        session.close()
        
        print("✅ Données d'exemple créées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données d'exemple: {str(e)}")
        return False

def backup_database(db_path=None):
    """Create a backup of the database"""
    print("💾 Création d'une sauvegarde...")
    
    try:
        db_manager = DatabaseManager(db_path)
        backup_path = db_manager.backup_database()
        print(f"✅ Sauvegarde créée: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {str(e)}")
        return False

def show_database_info(db_path=None):
    """Show database information and statistics"""
    print("📊 Informations sur la base de données...")
    
    try:
        db_manager = DatabaseManager(db_path)
        session = db_manager.get_session()
        
        # Count records
        user_count = session.query(User).count()
        patient_count = session.query(Patient).count()
        visit_count = session.query(Visit).count()
        
        # Calculate statistics
        total_revenue = session.query(Visit).with_entities(
            session.query(Visit.prix).filter(Visit.prix.isnot(None)).subquery().c.prix
        ).all()
        total_revenue = sum(price[0] for price in total_revenue if price[0])
        
        total_paid = session.query(Visit).with_entities(
            session.query(Visit.paye).filter(Visit.paye.isnot(None)).subquery().c.paye
        ).all()
        total_paid = sum(paid[0] for paid in total_paid if paid[0])
        
        total_unpaid = session.query(Visit).with_entities(
            session.query(Visit.reste).filter(Visit.reste > 0).subquery().c.reste
        ).all()
        total_unpaid = sum(unpaid[0] for unpaid in total_unpaid if unpaid[0])
        
        session.close()
        
        print(f"📍 Emplacement: {db_manager.db_path}")
        print(f"👥 Utilisateurs: {user_count}")
        print(f"🏥 Patients: {patient_count}")
        print(f"📅 Visites: {visit_count}")
        print(f"💰 Chiffre d'affaires total: {total_revenue:.2f} DH")
        print(f"✅ Total payé: {total_paid:.2f} DH")
        print(f"⏳ Total impayé: {total_unpaid:.2f} DH")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des informations: {str(e)}")
        return False

def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(description='DentisteDB Database Management')
    parser.add_argument('--db-path', help='Path to database file')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--reset', action='store_true', help='Reset database (delete existing data)')
    parser.add_argument('--sample-data', action='store_true', help='Create sample data')
    parser.add_argument('--backup', action='store_true', help='Create database backup')
    parser.add_argument('--info', action='store_true', help='Show database information')
    
    args = parser.parse_args()
    
    if not any([args.init, args.sample_data, args.backup, args.info]):
        parser.print_help()
        return
    
    print("🏥 DentisteDB - Gestionnaire de Base de Données")
    print("=" * 50)
    
    success = True
    
    if args.init:
        success &= init_database(args.db_path, args.reset)
    
    if args.sample_data and success:
        success &= create_sample_data(args.db_path)
    
    if args.backup and success:
        success &= backup_database(args.db_path)
    
    if args.info:
        success &= show_database_info(args.db_path)
    
    if success:
        print("\n🎉 Opération(s) terminée(s) avec succès!")
    else:
        print("\n❌ Une ou plusieurs opérations ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()
