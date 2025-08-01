"""
Patient service for handling patient-related business logic
Migrated from Flask routes to standalone service class
"""

from ..models.database import Patient, DatabaseManager
from sqlalchemy import or_
from typing import List, Optional, Tuple
import os
import shutil
from datetime import datetime

class PatientService:
    """Service for handling patient operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.xray_folder = os.path.expanduser("~/.dentistedb/xrays")
        os.makedirs(self.xray_folder, exist_ok=True)
    
    def get_all_patients(self) -> List[Patient]:
        """Get all patients from database"""
        session = self.db_manager.get_session()
        try:
            # Query patients directly without relationships to avoid session issues
            results = session.query(
                Patient.id,
                Patient.nom,
                Patient.prenom,
                Patient.date_naissance,
                Patient.telephone,
                Patient.numero_carte_national,
                Patient.assurance,
                Patient.profession,
                Patient.maladie,
                Patient.observation,
                Patient.xray_photo,
                Patient.created_at
            ).all()
            
            # Create patient objects
            patients = []
            for row in results:
                patient = Patient(
                    id=row[0],
                    nom=row[1],
                    prenom=row[2],
                    date_naissance=row[3],
                    telephone=row[4],
                    numero_carte_national=row[5],
                    assurance=row[6],
                    profession=row[7],
                    maladie=row[8],
                    observation=row[9],
                    xray_photo=row[10],
                    created_at=row[11]
                )
                patients.append(patient)
            
            return patients
        finally:
            session.close()
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        session = self.db_manager.get_session()
        try:
            # Query patient directly without relationships to avoid session issues
            result = session.query(
                Patient.id,
                Patient.nom,
                Patient.prenom,
                Patient.date_naissance,
                Patient.telephone,
                Patient.numero_carte_national,
                Patient.assurance,
                Patient.profession,
                Patient.maladie,
                Patient.observation,
                Patient.xray_photo,
                Patient.created_at
            ).filter_by(id=patient_id).first()
            
            if result:
                patient = Patient(
                    id=result[0],
                    nom=result[1],
                    prenom=result[2],
                    date_naissance=result[3],
                    telephone=result[4],
                    numero_carte_national=result[5],
                    assurance=result[6],
                    profession=result[7],
                    maladie=result[8],
                    observation=result[9],
                    xray_photo=result[10],
                    created_at=result[11]
                )
                return patient
            return None
        finally:
            session.close()
    
    def search_patients(self, query: str) -> List[Patient]:
        """Search patients by name, phone, or national card number"""
        if not query.strip():
            return self.get_all_patients()
        
        session = self.db_manager.get_session()
        try:
            search_term = f"%{query.strip()}%"
            results = session.query(
                Patient.id,
                Patient.nom,
                Patient.prenom,
                Patient.date_naissance,
                Patient.telephone,
                Patient.numero_carte_national,
                Patient.assurance,
                Patient.profession,
                Patient.maladie,
                Patient.observation,
                Patient.xray_photo,
                Patient.created_at
            ).filter(
                or_(
                    Patient.nom.ilike(search_term),
                    Patient.prenom.ilike(search_term),
                    Patient.telephone.ilike(search_term),
                    Patient.numero_carte_national.ilike(search_term)
                )
            ).all()
            
            # Create patient objects
            patients = []
            for row in results:
                patient = Patient(
                    id=row[0],
                    nom=row[1],
                    prenom=row[2],
                    date_naissance=row[3],
                    telephone=row[4],
                    numero_carte_national=row[5],
                    assurance=row[6],
                    profession=row[7],
                    maladie=row[8],
                    observation=row[9],
                    xray_photo=row[10],
                    created_at=row[11]
                )
                patients.append(patient)
            
            return patients
        finally:
            session.close()
    
    def create_patient(self, patient_data: dict) -> Tuple[bool, str, Optional[Patient]]:
        """
        Create a new patient
        Returns (success, message, patient)
        """
        session = self.db_manager.get_session()
        try:
            new_patient = Patient(
                nom=patient_data.get('nom', '').strip(),
                prenom=patient_data.get('prenom', '').strip(),
                date_naissance=patient_data.get('date_naissance'),
                telephone=patient_data.get('telephone', '').strip(),
                numero_carte_national=patient_data.get('numero_carte_national', '').strip(),
                assurance=patient_data.get('assurance', '').strip(),
                profession=patient_data.get('profession', '').strip(),
                maladie=patient_data.get('maladie', '').strip(),
                observation=patient_data.get('observation', '').strip()
            )
            
            session.add(new_patient)
            session.commit()
            
            # Refresh to get the ID
            session.refresh(new_patient)
            
            return True, f"Patient {new_patient.full_name} créé avec succès", new_patient
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la création du patient: {str(e)}", None
        finally:
            session.close()
    
    def update_patient(self, patient_id: int, patient_data: dict) -> Tuple[bool, str]:
        """
        Update an existing patient
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                return False, "Patient non trouvé"
            
            # Update fields
            patient.nom = patient_data.get('nom', '').strip()
            patient.prenom = patient_data.get('prenom', '').strip()
            patient.date_naissance = patient_data.get('date_naissance')
            patient.telephone = patient_data.get('telephone', '').strip()
            patient.numero_carte_national = patient_data.get('numero_carte_national', '').strip()
            patient.assurance = patient_data.get('assurance', '').strip()
            patient.profession = patient_data.get('profession', '').strip()
            patient.maladie = patient_data.get('maladie', '').strip()
            patient.observation = patient_data.get('observation', '').strip()
            
            session.commit()
            
            return True, f"Patient {patient.full_name} mis à jour avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la mise à jour du patient: {str(e)}"
        finally:
            session.close()
    
    def delete_patient(self, patient_id: int) -> Tuple[bool, str]:
        """
        Delete a patient and all associated data
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                return False, "Patient non trouvé"
            
            patient_name = patient.full_name
            
            # Delete X-ray file if exists
            if patient.xray_photo:
                xray_path = os.path.join(self.xray_folder, patient.xray_photo)
                if os.path.exists(xray_path):
                    os.remove(xray_path)
            
            # Delete patient (visits will be deleted due to cascade)
            session.delete(patient)
            session.commit()
            
            return True, f"Patient {patient_name} supprimé avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la suppression du patient: {str(e)}"
        finally:
            session.close()
    
    def upload_xray(self, patient_id: int, file_path: str) -> Tuple[bool, str]:
        """
        Upload X-ray image for a patient
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                return False, "Patient non trouvé"
            
            if not os.path.exists(file_path):
                return False, "Fichier non trouvé"
            
            # Get file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in ['.png', '.jpg', '.jpeg']:
                return False, "Type de fichier non autorisé. Utilisez PNG, JPG ou JPEG."
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"xray_{patient_id}_{timestamp}{ext.lower()}"
            destination = os.path.join(self.xray_folder, filename)
            
            # Delete old X-ray if exists
            if patient.xray_photo:
                old_path = os.path.join(self.xray_folder, patient.xray_photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Copy new file
            shutil.copy2(file_path, destination)
            
            # Update patient record
            patient.xray_photo = filename
            session.commit()
            
            return True, "Radiographie téléchargée avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors du téléchargement: {str(e)}"
        finally:
            session.close()
    
    def delete_xray(self, patient_id: int) -> Tuple[bool, str]:
        """
        Delete X-ray image for a patient
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                return False, "Patient non trouvé"
            
            if not patient.xray_photo:
                return False, "Aucune radiographie à supprimer"
            
            # Delete file
            xray_path = os.path.join(self.xray_folder, patient.xray_photo)
            if os.path.exists(xray_path):
                os.remove(xray_path)
            
            # Clear database reference
            patient.xray_photo = None
            session.commit()
            
            return True, "Radiographie supprimée avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la suppression: {str(e)}"
        finally:
            session.close()
    
    def get_xray_path(self, patient_id: int) -> Optional[str]:
        """Get the full path to patient's X-ray image"""
        session = self.db_manager.get_session()
        try:
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if patient and patient.xray_photo:
                xray_path = os.path.join(self.xray_folder, patient.xray_photo)
                if os.path.exists(xray_path):
                    return xray_path
            return None
        finally:
            session.close()
    
    def get_patients_with_unpaid_balances(self) -> List[Patient]:
        """Get patients who have unpaid visit balances"""
        session = self.db_manager.get_session()
        try:
            # Get patients with unpaid visits using a subquery
            from ..models.database import Visit
            subquery = session.query(Visit.patient_id).filter(Visit.reste > 0).distinct().subquery()
            
            results = session.query(
                Patient.id,
                Patient.nom,
                Patient.prenom,
                Patient.date_naissance,
                Patient.telephone,
                Patient.numero_carte_national,
                Patient.assurance,
                Patient.profession,
                Patient.maladie,
                Patient.observation,
                Patient.xray_photo,
                Patient.created_at
            ).filter(
                Patient.id.in_(session.query(subquery.c.patient_id))
            ).all()
            
            # Create patient objects
            patients = []
            for row in results:
                patient = Patient(
                    id=row[0],
                    nom=row[1],
                    prenom=row[2],
                    date_naissance=row[3],
                    telephone=row[4],
                    numero_carte_national=row[5],
                    assurance=row[6],
                    profession=row[7],
                    maladie=row[8],
                    observation=row[9],
                    xray_photo=row[10],
                    created_at=row[11]
                )
                patients.append(patient)
            
            return patients
        finally:
            session.close()
