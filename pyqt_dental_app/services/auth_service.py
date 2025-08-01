"""
Authentication service for handling user login and session management
Migrated from Flask-Login to custom session management for PyQt
"""

from ..models.database import User, DatabaseManager
from typing import Optional

class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_user: Optional[User] = None
        self.is_authenticated = False
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate user with username and password
        Returns (success, message)
        """
        if not username or not password:
            return False, "Veuillez remplir tous les champs"
        
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            
            if not user:
                return False, "Utilisateur non trouvé. Vérifiez votre nom d'utilisateur ou contactez l'administrateur."
            
            if not user.check_password(password):
                return False, "Mot de passe incorrect. Veuillez réessayer."
            
            if not user.is_active:
                return False, "Compte utilisateur désactivé. Contactez l'administrateur."
            
            # Set current user
            self.current_user = user
            self.is_authenticated = True
            
            return True, f"Connexion réussie. Bienvenue {user.username}!"
            
        finally:
            session.close()
    
    def logout(self):
        """Clear current user session"""
        self.current_user = None
        self.is_authenticated = False
    
    def get_current_user(self) -> Optional[User]:
        """Get currently authenticated user"""
        return self.current_user
    
    def is_user_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.is_authenticated and self.current_user is not None
    
    def create_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Create a new user (admin function)
        Returns (success, message)
        """
        if not username or not password:
            return False, "Nom d'utilisateur et mot de passe requis"
        
        session = self.db_manager.get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                return False, "Un utilisateur avec ce nom existe déjà"
            
            # Create new user
            new_user = User(username=username)
            new_user.set_password(password)
            session.add(new_user)
            session.commit()
            
            return True, f"Utilisateur {username} créé avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors de la création de l'utilisateur: {str(e)}"
        finally:
            session.close()
    
    def change_password(self, old_password: str, new_password: str) -> tuple[bool, str]:
        """
        Change password for current user
        Returns (success, message)
        """
        if not self.is_authenticated:
            return False, "Vous devez être connecté pour changer le mot de passe"
        
        if not old_password or not new_password:
            return False, "Ancien et nouveau mot de passe requis"
        
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(id=self.current_user.id).first()
            
            if not user.check_password(old_password):
                return False, "Ancien mot de passe incorrect"
            
            user.set_password(new_password)
            session.commit()
            
            return True, "Mot de passe changé avec succès"
            
        except Exception as e:
            session.rollback()
            return False, f"Erreur lors du changement de mot de passe: {str(e)}"
        finally:
            session.close()
