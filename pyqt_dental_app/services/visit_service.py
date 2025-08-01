"""
Visit service for handling visit-related business logic
Migrated from Flask routes to standalone service class
"""

from ..models.database import Visit, Patient, DatabaseManager
from typing import List, Optional, Tuple
from datetime import datetime, date

class VisitService:
    """Service for handling visit operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_visits_for_patient(self, patient_id: int) -> List[Visit]:
        """Get all visits for a specific patient"""
        session = self.db_manager.get_session()
        try:
            # Query visits directly without relationships to avoid session issues
            results = session.query(
                Visit.id,
                Visit.date,
                Visit.dent,
                Visit.acte,
                Visit.prix,
                Visit.paye,
                Visit.reste,
                Visit.patient_id
            ).filter_by(patient_id=patient_id).order_by(Visit.date.desc()).all()
            
            # Create visit objects
            visits = []
            for row in results:
                prix = row[4] or 0.0
                paye = row[5] or 0.0
                reste = prix - paye  # Always calculate reste to ensure accuracy
                
                visit = Visit(
                    id=row[0],
                    date=row[1],
                    dent=row[2],
                    acte=row[3],
                    prix=prix,
                    paye=paye,
                    reste=reste,
                    patient_id=row[7]
                )
                visits.append(visit)
            
            return visits
        finally:
            session.close()
    
    def get_visit_by_id(self, visit_id: int) -> Optional[Visit]:
        """Get visit by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit).filter_by(id=visit_id).first()
        finally:
            session.close()
    
    def create_visit(self, patient_id: int, visit_data: dict) -> Tuple[bool, str, Optional[Visit]]:
        """
        Create a new visit for a patient
        Returns (success, message, visit)
        """
        session = self.db_manager.get_session()
        try:
            # Verify patient exists
            patient = session.query(Patient).filter_by(id=patient_id).first()
            if not patient:
                return False, "Patient non trouvé", None
            
            # Parse and validate data
            try:
                visit_date = datetime.strptime(visit_data.get('date', ''), '%Y-%m-%d').date() if visit_data.get('date') else date.today()
            except ValueError:
                visit_date = date.today()
            
            try:
                prix = float(visit_data.get('prix', 0)) if visit_data.get('prix') else 0.0
                paye = float(visit_data.get('paye', 0)) if visit_data.get('paye') else 0.0
            except ValueError:
                prix = 0.0
                paye = 0.0
            
            # Create new visit
            new_visit = Visit(
                patient_id=patient_id,
                date=visit_date,
                dent=visit_data.get('dent', '').strip(),
                acte=visit_data.get('acte', '').strip(),
                prix=prix,
                paye=paye,
                reste=prix - paye
            )
            
            session.add(new_visit)
            session.commit()
            
            # Refresh to get the ID
            session.refresh(new_visit)
            
            return True, f"Visite créée avec succès pour {patient.full_name}", new_visit
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la création de la visite: {str(e)}", None
        finally:
            session.close()
    
    def update_visit(self, visit_id: int, visit_data: dict) -> Tuple[bool, str]:
        """
        Update an existing visit
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            visit = session.query(Visit).filter_by(id=visit_id).first()
            if not visit:
                return False, "Visite non trouvée"
            
            # Parse and validate data
            try:
                visit_date = datetime.strptime(visit_data.get('date', ''), '%Y-%m-%d').date() if visit_data.get('date') else visit.date
            except ValueError:
                visit_date = visit.date
            
            try:
                prix = float(visit_data.get('prix', 0)) if visit_data.get('prix') else 0.0
                paye = float(visit_data.get('paye', 0)) if visit_data.get('paye') else 0.0
            except ValueError:
                prix = visit.prix or 0.0
                paye = visit.paye or 0.0
            
            # Update fields
            visit.date = visit_date
            visit.dent = visit_data.get('dent', '').strip()
            visit.acte = visit_data.get('acte', '').strip()
            visit.prix = prix
            visit.paye = paye
            visit.reste = prix - paye
            
            session.commit()
            
            return True, "Visite mise à jour avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la mise à jour de la visite: {str(e)}"
        finally:
            session.close()
    
    def delete_visit(self, visit_id: int) -> Tuple[bool, str]:
        """
        Delete a visit
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            visit = session.query(Visit).filter_by(id=visit_id).first()
            if not visit:
                return False, "Visite non trouvée"
            
            session.delete(visit)
            session.commit()
            
            return True, "Visite supprimée avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la suppression de la visite: {str(e)}"
        finally:
            session.close()
    
    def get_all_unpaid_visits(self) -> List[Visit]:
        """Get all visits with unpaid balances"""
        session = self.db_manager.get_session()
        try:
            # Query visits with unpaid balances and join with patient data
            from ..models.database import Patient
            results = session.query(
                Visit.id,
                Visit.date,
                Visit.dent,
                Visit.acte,
                Visit.prix,
                Visit.paye,
                Visit.reste,
                Visit.patient_id,
                Patient.nom,
                Patient.prenom,
                Patient.telephone,
                Patient.numero_carte_national,
                Patient.assurance,
                Patient.profession,
                Patient.maladie,
                Patient.observation,
                Patient.xray_photo
            ).join(Patient).filter(Visit.reste > 0).order_by(Visit.date.desc()).all()
            
            # Create visit objects with patient data
            visits = []
            for row in results:
                prix = row[4] or 0.0
                paye = row[5] or 0.0
                reste = prix - paye  # Always calculate reste to ensure accuracy
                
                visit = Visit(
                    id=row[0],
                    date=row[1],
                    dent=row[2],
                    acte=row[3],
                    prix=prix,
                    paye=paye,
                    reste=reste,
                    patient_id=row[7]
                )
                
                # Create patient object
                patient = Patient(
                    id=row[7],
                    nom=row[8],
                    prenom=row[9],
                    telephone=row[10],
                    numero_carte_national=row[11],
                    assurance=row[12],
                    profession=row[13],
                    maladie=row[14],
                    observation=row[15],
                    xray_photo=row[16]
                )
                
                # Set the relationship manually
                visit.patient = patient
                visits.append(visit)
            
            return visits
        finally:
            session.close()
    
    def get_visits_by_date_range(self, start_date: date, end_date: date) -> List[Visit]:
        """Get visits within a date range"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit).filter(
                Visit.date >= start_date,
                Visit.date <= end_date
            ).order_by(Visit.date.desc()).all()
        finally:
            session.close()
    
    def get_total_revenue(self, start_date: date = None, end_date: date = None) -> dict:
        """
        Calculate total revenue statistics
        Returns dict with total_earned, total_pending, total_visits
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(Visit)
            
            if start_date:
                query = query.filter(Visit.date >= start_date)
            if end_date:
                query = query.filter(Visit.date <= end_date)
            
            visits = query.all()
            
            total_earned = sum(visit.paye or 0 for visit in visits)
            total_pending = sum(visit.reste or 0 for visit in visits)
            total_visits = len(visits)
            total_revenue = sum(visit.prix or 0 for visit in visits)
            
            return {
                'total_earned': total_earned,
                'total_pending': total_pending,
                'total_revenue': total_revenue,
                'total_visits': total_visits
            }
        finally:
            session.close()
    
    def mark_visit_as_paid(self, visit_id: int) -> Tuple[bool, str]:
        """
        Mark a visit as fully paid
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            visit = session.query(Visit).filter_by(id=visit_id).first()
            if not visit:
                return False, "Visite non trouvée"
            
            visit.paye = visit.prix or 0.0
            visit.reste = 0.0
            session.commit()
            
            return True, "Visite marquée comme payée"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la mise à jour du paiement: {str(e)}"
        finally:
            session.close()
    
    def add_payment(self, visit_id: int, payment_amount: float) -> Tuple[bool, str]:
        """
        Add a payment to an existing visit
        Returns (success, message)
        """
        session = self.db_manager.get_session()
        try:
            visit = session.query(Visit).filter_by(id=visit_id).first()
            if not visit:
                return False, "Visite non trouvée"
            
            if payment_amount <= 0:
                return False, "Le montant du paiement doit être positif"
            
            new_paye = (visit.paye or 0.0) + payment_amount
            if new_paye > (visit.prix or 0.0):
                return False, "Le paiement total ne peut pas dépasser le prix de la visite"
            
            visit.paye = new_paye
            visit.reste = (visit.prix or 0.0) - new_paye
            session.commit()
            
            return True, f"Paiement de {payment_amount:.2f} ajouté avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de l'ajout du paiement: {str(e)}"
        finally:
            session.close()
