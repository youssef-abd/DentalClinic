"""
Tooth service for managing dental chart and tooth status operations
Handles CRUD operations for individual tooth conditions and dental chart management
"""

from typing import List, Optional, Dict
from datetime import datetime
from ..models.database import ToothStatus

class ToothService:
    """Service for managing tooth status and dental chart operations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_patient_tooth_chart(self, patient_id: int) -> Dict[int, str]:
        """Get complete tooth chart for a patient as a dictionary {tooth_number: status}"""
        session = self.db_manager.get_session()
        try:
            # Query all tooth statuses for the patient
            results = session.query(
                ToothStatus.tooth_number,
                ToothStatus.status
            ).filter_by(patient_id=patient_id).all()
            
            # Create a complete tooth chart (1-32) with default 'normal' status
            tooth_chart = {}
            for tooth_num in range(1, 33):  # Adult teeth 1-32
                tooth_chart[tooth_num] = 'normal'
            
            # Update with actual statuses from database
            for tooth_number, status in results:
                tooth_chart[tooth_number] = status
            
            return tooth_chart
        finally:
            session.close()
    
    def update_tooth_status(self, patient_id: int, tooth_number: int, status: str, notes: str = None) -> bool:
        """Update or create tooth status for a specific tooth"""
        if tooth_number < 1 or tooth_number > 32:
            return False
        
        session = self.db_manager.get_session()
        try:
            # Check if tooth status already exists
            existing = session.query(ToothStatus).filter_by(
                patient_id=patient_id, 
                tooth_number=tooth_number
            ).first()
            
            if existing:
                # Update existing record
                existing.status = status
                existing.notes = notes
                existing.date_recorded = datetime.now().date()
            else:
                # Create new record
                tooth_status = ToothStatus(
                    patient_id=patient_id,
                    tooth_number=tooth_number,
                    status=status,
                    notes=notes
                )
                session.add(tooth_status)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error updating tooth status: {e}")
            return False
        finally:
            session.close()
    
    def get_tooth_status(self, patient_id: int, tooth_number: int) -> Optional[str]:
        """Get status of a specific tooth"""
        session = self.db_manager.get_session()
        try:
            result = session.query(ToothStatus.status).filter_by(
                patient_id=patient_id,
                tooth_number=tooth_number
            ).first()
            
            return result[0] if result else 'normal'
        finally:
            session.close()
    
    def get_tooth_details(self, patient_id: int, tooth_number: int) -> Optional[Dict]:
        """Get detailed information about a specific tooth"""
        session = self.db_manager.get_session()
        try:
            result = session.query(
                ToothStatus.status,
                ToothStatus.notes,
                ToothStatus.date_recorded
            ).filter_by(
                patient_id=patient_id,
                tooth_number=tooth_number
            ).first()
            
            if result:
                return {
                    'status': result[0],
                    'notes': result[1],
                    'date_recorded': result[2]
                }
            else:
                return {
                    'status': 'normal',
                    'notes': None,
                    'date_recorded': None
                }
        finally:
            session.close()
    
    def get_teeth_by_status(self, patient_id: int, status: str) -> List[int]:
        """Get list of tooth numbers with a specific status"""
        session = self.db_manager.get_session()
        try:
            results = session.query(ToothStatus.tooth_number).filter_by(
                patient_id=patient_id,
                status=status
            ).all()
            
            return [result[0] for result in results]
        finally:
            session.close()
    
    def get_dental_summary(self, patient_id: int) -> Dict[str, int]:
        """Get summary of dental conditions for a patient"""
        session = self.db_manager.get_session()
        try:
            # Count teeth by status
            results = session.query(
                ToothStatus.status,
                session.query(ToothStatus).filter_by(patient_id=patient_id, status=ToothStatus.status).count()
            ).filter_by(patient_id=patient_id).group_by(ToothStatus.status).all()
            
            summary = {
                'normal': 32,  # Start with all teeth normal
                'carie': 0,
                'couronne': 0,
                'bridge': 0,
                'implant': 0,
                'extraction': 0,
                'other': 0
            }
            
            total_affected = 0
            for status, count in results:
                if status in summary:
                    summary[status] = count
                    if status != 'normal':
                        total_affected += count
                else:
                    summary['other'] += count
                    total_affected += count
            
            # Adjust normal count
            summary['normal'] = 32 - total_affected
            
            return summary
        finally:
            session.close()
    
    @staticmethod
    def get_available_statuses() -> List[Dict[str, str]]:
        """Get list of available tooth statuses with their display names and colors"""
        return [
            {'key': 'normal', 'name': 'Normal', 'color': '#E5E7EB'},
            {'key': 'carie', 'name': 'Carie', 'color': '#EF4444'},
            {'key': 'couronne', 'name': 'Couronne', 'color': '#3B82F6'},
            {'key': 'obturation', 'name': 'Obturation', 'color': '#8B5CF6'},
            {'key': 'implant', 'name': 'Implant', 'color': '#10B981'},
            {'key': 'obturation canalaire', 'name': 'Obturation Canalaire', 'color': '#6B7280'},
            {'key': 'dent absente', 'name': 'Dent Absente', 'color': '#F59E0B'},
            {'key': 'tartre', 'name': 'Tartre', 'color': '#EC4899'}
        ]
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for a specific tooth status"""
        status_colors = {
            'normal': '#E5E7EB',
            'carie': '#EF4444',
            'couronne': '#3B82F6',
            'obturation': '#8B5CF6',
            'implant': '#10B981',
            'obturation canalaire': '#6B7280',
            'dent absente': '#F59E0B',
            'tartre': '#EC4899'
        }
        return status_colors.get(status, '#E5E7EB')
