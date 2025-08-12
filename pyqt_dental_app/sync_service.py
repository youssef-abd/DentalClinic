# sync_service.py
import os
import sys
import time
import threading
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_to_supabase import run_sync, get_last_sync_timestamp, supabase  # Import your existing sync functions

class SyncStatus(Enum):
    IDLE = "idle"
    SYNCING = "syncing" 
    SUCCESS = "success"
    ERROR = "error"
    SCHEDULED = "scheduled"

@dataclass
class SyncResult:
    status: SyncStatus
    message: str
    timestamp: datetime
    patients_synced: int = 0
    visits_synced: int = 0
    error: Optional[str] = None

class SyncService:
    def __init__(self, sync_interval_minutes: int = 30):
        self.sync_interval = sync_interval_minutes * 60  # Convert to seconds
        self.is_running = False
        self.sync_thread = None
        self.current_status = SyncStatus.IDLE
        self.last_result: Optional[SyncResult] = SyncResult(
            status=SyncStatus.IDLE,
            message="Service initialized",
            timestamp=datetime.now()
        )
        self.status_callbacks = []  # UI callbacks to notify of status changes
        self.auto_sync_enabled = True
        
    def add_status_callback(self, callback: Callable[[SyncResult], None]):
        """Add callback function to be notified of sync status changes"""
        try:
            if callback not in self.status_callbacks:
                self.status_callbacks.append(callback)
        except Exception as e:
            print(f"Error adding status callback: {e}")
    
    def remove_status_callback(self, callback: Callable[[SyncResult], None]):
        """Remove a status callback"""
        try:
            if callback in self.status_callbacks:
                self.status_callbacks.remove(callback)
        except Exception as e:
            print(f"Error removing status callback: {e}")
    
    def _notify_status_change(self, result: SyncResult):
        """Notify all callbacks of status change"""
        try:
            self.last_result = result
            self.current_status = result.status
            for callback in self.status_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    print(f"Error in status callback: {e}")
        except Exception as e:
            print(f"Error in _notify_status_change: {e}")
    
    def start_background_sync(self):
        """Start the background sync service"""
        if self.is_running:
            print("Sync service is already running")
            return
        
        try:
            # Test database connection before starting
            from pyqt_dental_app.models.database import DatabaseManager
            db_manager = DatabaseManager()
            session = db_manager.get_session()
            session.close()
            print("Database connection test successful")
        except Exception as e:
            print(f"Database connection test failed: {e}")
            # Still start the service, but it will handle errors gracefully
            
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        # Notify that service is scheduled
        self._notify_status_change(SyncResult(
            status=SyncStatus.SCHEDULED,
            message="Background sync service started",
            timestamp=datetime.now()
        ))
        
    def stop_background_sync(self):
        """Stop the background sync service"""
        try:
            self.is_running = False
            if self.sync_thread and self.sync_thread.is_alive():
                print("Waiting for sync thread to stop...")
                self.sync_thread.join(timeout=5)
                if self.sync_thread.is_alive():
                    print("Warning: Sync thread did not stop within timeout")
            
            self._notify_status_change(SyncResult(
                status=SyncStatus.IDLE,
                message="Background sync service stopped",
                timestamp=datetime.now()
            ))
        except Exception as e:
            print(f"Error stopping background sync: {e}")
    
    def _sync_loop(self):
        """Main sync loop that runs in background thread"""
        print("Background sync service started")
        
        while self.is_running:
            try:
                if self.auto_sync_enabled:
                    print("Starting scheduled sync...")
                    result = self.sync_now()
                    if result.status == SyncStatus.SUCCESS:
                        print(f"Scheduled sync completed: {result.patients_synced} patients, {result.visits_synced} visits")
                    else:
                        print(f"Scheduled sync failed: {result.message}")
                
                # Wait for next sync, but check every 10 seconds if we should stop
                wait_time = 0
                while wait_time < self.sync_interval and self.is_running:
                    time.sleep(10)
                    wait_time += 10
            except Exception as e:
                print(f"Error in background sync loop: {e}")
                # Wait a bit before retrying
                time.sleep(60)
    
    def sync_now(self, force: bool = False) -> SyncResult:
        """Trigger immediate sync"""
        if self.current_status == SyncStatus.SYNCING and not force:
            return self.last_result or SyncResult(
                status=SyncStatus.SYNCING,
                message="Sync already in progress",
                timestamp=datetime.now()
            )
        
        # Notify sync started
        self._notify_status_change(SyncResult(
            status=SyncStatus.SYNCING,
            message="Synchronization in progress...",
            timestamp=datetime.now()
        ))
        
        try:
            # Call your existing sync function
            result = self._perform_sync()
            self._notify_status_change(result)
            return result
            
        except Exception as e:
            print(f"Error in sync_now: {e}")
            error_result = SyncResult(
                status=SyncStatus.ERROR,
                message=f"Sync failed: {str(e)}",
                timestamp=datetime.now(),
                error=str(e)
            )
            self._notify_status_change(error_result)
            return error_result
    
    def _perform_sync(self) -> SyncResult:
        """Perform the actual sync operation"""
        start_time = datetime.now()
        
        try:
            # Get counts before sync
            patients_last_sync = get_last_sync_timestamp('patients')
            visits_last_sync = get_last_sync_timestamp('visits')
            
            # Perform sync (modify your existing run_sync function to return counts)
            patients_synced, visits_synced = self._run_sync_with_counts()
            
            if patients_synced >= 0 and visits_synced >= 0:  # Success
                return SyncResult(
                    status=SyncStatus.SUCCESS,
                    message=f"Sync completed successfully",
                    timestamp=start_time,
                    patients_synced=patients_synced,
                    visits_synced=visits_synced
                )
            else:
                return SyncResult(
                    status=SyncStatus.ERROR,
                    message="Sync failed",
                    timestamp=start_time,
                    error="Unknown sync error"
                )
        except Exception as e:
            print(f"Error in _perform_sync: {e}")
            return SyncResult(
                status=SyncStatus.ERROR,
                message=f"Sync failed: {str(e)}",
                timestamp=start_time,
                error=str(e)
            )
    
    def _run_sync_with_counts(self):
        """Modified version of run_sync that returns counts"""
        try:
            # Use the existing sync functions from sync_to_supabase
            from sync_to_supabase import sync_patients, sync_visits
            from pyqt_dental_app.models.database import DatabaseManager
            
            # Get database session through DatabaseManager
            db_manager = DatabaseManager()
            session = db_manager.get_session()
            
            try:
                # Get counts before sync
                patients_last_sync = get_last_sync_timestamp('patients')
                visits_last_sync = get_last_sync_timestamp('visits')
                
                # Count records to sync
                from pyqt_dental_app.models.database import Patient, Visit
                
                # Check if tables exist and have data
                try:
                    patients_to_sync = session.query(Patient).filter(
                        Patient.updated_at > patients_last_sync.date()
                    ).count()
                except Exception as e:
                    print(f"Error counting patients: {e}")
                    patients_to_sync = 0
                
                try:
                    visits_to_sync = session.query(Visit).filter(
                        Visit.updated_at > visits_last_sync.date()
                    ).count()
                except Exception as e:
                    print(f"Error counting visits: {e}")
                    visits_to_sync = 0
                
                # Perform the actual sync
                try:
                    patients_success, patients_count, _ = sync_patients(session, supabase, silent=True)
                except Exception as e:
                    print(f"Error syncing patients: {e}")
                    patients_success, patients_count = False, 0
                
                try:
                    visits_success, visits_count, _ = sync_visits(session, supabase, silent=True)
                except Exception as e:
                    print(f"Error syncing visits: {e}")
                    visits_success, visits_count = False, 0
                
                if patients_success and visits_success:
                    return patients_count, visits_count
                else:
                    return -1, -1  # Error indicator
                    
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error in _run_sync_with_counts: {e}")
            return -1, -1
    

    
    def get_sync_status(self) -> dict:
        """Get current sync status for UI display"""
        try:
            return {
                'status': self.current_status.value,
                'is_running': self.is_running,
                'auto_sync_enabled': self.auto_sync_enabled,
                'last_result': {
                    'status': self.last_result.status.value,
                    'message': self.last_result.message,
                    'timestamp': self.last_result.timestamp.isoformat(),
                    'patients_synced': self.last_result.patients_synced,
                    'visits_synced': self.last_result.visits_synced,
                    'error': self.last_result.error
                },
                'sync_interval_minutes': self.sync_interval // 60
            }
        except Exception as e:
            print(f"Error in get_sync_status: {e}")
            return {
                'status': 'error',
                'is_running': False,
                'auto_sync_enabled': False,
                'last_result': None,
                'sync_interval_minutes': 30
            }
    
    def set_auto_sync(self, enabled: bool):
        """Enable/disable automatic syncing"""
        try:
            self.auto_sync_enabled = enabled
            print(f"Auto sync {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            print(f"Error setting auto sync: {e}")
    
    def set_sync_interval(self, minutes: int):
        """Change sync interval"""
        try:
            self.sync_interval = minutes * 60
            print(f"Sync interval set to {minutes} minutes")
        except Exception as e:
            print(f"Error setting sync interval: {e}")


# Global sync service instance
sync_service = SyncService(sync_interval_minutes=30)


# Example usage functions
def start_sync_service():
    """Start the background sync service - call this from your main app"""
    try:
        sync_service.start_background_sync()
        print("Sync service started successfully")
    except Exception as e:
        print(f"Error starting sync service: {e}")

def stop_sync_service():
    """Stop the background sync service - call this when app closes"""
    try:
        sync_service.stop_background_sync()
        print("Sync service stopped successfully")
    except Exception as e:
        print(f"Error stopping sync service: {e}")

def trigger_manual_sync():
    """Trigger manual sync from UI"""
    try:
        return sync_service.sync_now()
    except Exception as e:
        print(f"Error triggering manual sync: {e}")
        return None

def get_sync_status():
    """Get current sync status for UI"""
    try:
        return sync_service.get_sync_status()
    except Exception as e:
        print(f"Error getting sync status: {e}")
        return None