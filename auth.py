"""""
Système d'authentification et autorisations - VERSION FINALE
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any

# Importer la base de données
from database import db_instance


class AuthManager:
    """Gestionnaire d'authentification complet avec sessions"""
    
    def __init__(self):
        self.current_user = None
        self.session_token = None
        self.session_start_time = None
        self.session_timeout = 3600  # 1 heure en secondes
    
    def login(self, employee_id: str, password: str) -> Optional[Dict]:
        """Authentifier un utilisateur - Version robuste"""
        try:
            print(f"\n{'='*60}")
            print(f"🔐 TENTATIVE DE CONNEXION: {employee_id}")
            print(f"{'='*60}")
            
            # Nettoyer les entrées
            employee_id = employee_id.strip()
            password = password.strip()
            
            if not employee_id:
                print("❌ ID employé vide")
                return None
            
            if not password:
                print("❌ Mot de passe vide")
                return None
            
            # Appeler l'authentification de la base de données
            user = db_instance.authenticate(employee_id, password)
            
            if user:
                print(f"\n✅ CONNEXION RÉUSSIE")
                print(f"   👤 Utilisateur: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"   🆔 ID: {user.get('employee_id')}")
                print(f"   🎭 Rôle: {user.get('role', 'N/A')}")
                print(f"   🏢 Département: {user.get('department_name', 'N/A')}")
                print(f"   📅 Dernière connexion: {user.get('last_login', 'Première connexion')}")
                
                # Initialiser la session
                self.current_user = user
                self.session_token = secrets.token_hex(32)
                self.session_start_time = datetime.now()
                
                return user
            else:
                print(f"\n❌ ÉCHEC DE CONNEXION")
                print(f"   Raison: ID ou mot de passe incorrect")
                return None
                
        except Exception as e:
            print(f"\n❌ ERREUR SYSTÈME LORS DE LA CONNEXION")
            print(f"   Détails: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def logout(self):
        """Déconnecter l'utilisateur courant"""
        if self.current_user:
            user_id = self.current_user.get('employee_id', 'Inconnu')
            user_name = f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}"
            print(f"\n👋 DÉCONNEXION: {user_name} ({user_id})")
        
        self.current_user = None
        self.session_token = None
        self.session_start_time = None
    
    def get_current_user(self) -> Optional[Dict]:
        """Obtenir l'utilisateur courant"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Vérifier si un utilisateur est authentifié"""
        if not self.current_user:
            return False
        
        # Vérifier le timeout de session
        if self.session_start_time:
            session_duration = (datetime.now() - self.session_start_time).total_seconds()
            
            if session_duration > self.session_timeout:
                print(f"\n⏰ SESSION EXPIRÉE ({session_duration:.0f}s > {self.session_timeout}s)")
                print(f"   Déconnexion automatique...")
                self.logout()
                return False
            
            # Avertir 5 minutes avant l'expiration
            if session_duration > (self.session_timeout - 300):  # 5 minutes avant
                remaining = self.session_timeout - session_duration
                print(f"⚠️  Session expire dans {remaining:.0f} secondes")
        
        return True
    
    def has_role(self, role: str) -> bool:
        """Vérifier si l'utilisateur a un rôle spécifique"""
        if not self.current_user:
            return False
        
        user_role = self.current_user.get('role', '').lower()
        return user_role == role.lower()
    
    def is_admin(self) -> bool:
        """Vérifier si l'utilisateur est administrateur"""
        return self.has_role('admin')
    
    def is_hr(self) -> bool:
        """Vérifier si l'utilisateur fait partie des RH"""
        return self.has_role('admin') or self.has_role('hr')
    
    def is_manager(self) -> bool:
        """Vérifier si l'utilisateur est manager"""
        return self.has_role('manager')
    
    def is_employee(self) -> bool:
        """Vérifier si l'utilisateur est un employé standard"""
        return self.has_role('employee')
    
    def can_manage_employees(self) -> bool:
        """Vérifier si l'utilisateur peut gérer les employés"""
        return self.is_admin() or self.is_hr()
    
    def can_approve_leaves(self) -> bool:
        """Vérifier si l'utilisateur peut approuver les congés"""
        return self.is_admin() or self.is_hr() or self.is_manager()
    
    def can_view_all_data(self) -> bool:
        """Vérifier si l'utilisateur peut voir toutes les données"""
        return self.is_admin()
    
    def can_view_sensitive_data(self) -> bool:
        """Vérifier si l'utilisateur peut voir les données sensibles"""
        return self.is_admin() or self.is_hr()
    
    def get_user_permissions(self) -> List[str]:
        """Obtenir les permissions de l'utilisateur"""
        if not self.current_user:
            return []
        
        role = self.current_user.get('role', 'employee').lower()
        
        permissions_map = {
            'admin': [
                'manage_all', 'view_all', 'edit_all', 'delete_all',
                'approve_all', 'export_all', 'system_settings',
                'backup_restore', 'manage_users', 'manage_roles',
                'view_audit_logs', 'manage_departments', 'manage_positions',
                'view_salaries', 'edit_salaries', 'manage_contracts'
            ],
            'hr': [
                'manage_employees', 'view_employees', 'edit_employees',
                'approve_leaves', 'view_leaves', 'export_data',
                'view_reports', 'manage_departments', 'view_salaries',
                'manage_contracts', 'view_attendance', 'manage_documents',
                'reset_passwords', 'view_profiles'
            ],
            'manager': [
                'view_team', 'approve_team_leaves', 'view_reports',
                'view_team_salaries', 'manage_team_schedule',
                'view_team_attendance', 'evaluate_team'
            ],
            'employee': [
                'view_own_profile', 'request_leave', 'view_own_leaves',
                'view_own_documents', 'update_own_info', 'view_own_attendance',
                'change_password', 'view_own_salary'
            ]
        }
        
        return permissions_map.get(role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Vérifier si l'utilisateur a une permission spécifique"""
        return permission in self.get_user_permissions()
    
    def get_user_info(self) -> Dict:
        """Obtenir les informations de l'utilisateur courant"""
        if not self.current_user:
            return {}
        
        user_info = {
            'employee_id': self.current_user.get('employee_id'),
            'full_name': f"{self.current_user.get('first_name', '')} {self.current_user.get('last_name', '')}",
            'role': self.current_user.get('role', 'employee'),
            'role_display': self._get_role_display(self.current_user.get('role', 'employee')),
            'department': self.current_user.get('department_name'),
            'position': self.current_user.get('position_title'),
            'email': self.current_user.get('work_email'),
            'phone': self.current_user.get('work_phone'),
            'last_login': self.current_user.get('last_login'),
            'hire_date': self.current_user.get('hire_date'),
            'is_active': self.current_user.get('is_active', False),
            'permissions': self.get_user_permissions(),
            'session_info': self.get_session_info()
        }
        
        return user_info
    
    def get_session_info(self) -> Dict:
        """Obtenir les informations de session"""
        if not self.session_start_time:
            return {}
        
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        expires_in = max(0, self.session_timeout - session_duration)
        
        return {
            'session_start': self.session_start_time.isoformat(),
            'session_duration_seconds': int(session_duration),
            'session_duration_formatted': self._format_duration(session_duration),
            'session_token': self.session_token[:8] + "..." if self.session_token else None,
            'expires_in_seconds': int(expires_in),
            'expires_in_formatted': self._format_duration(expires_in),
            'is_expired': session_duration > self.session_timeout,
            'timeout_seconds': self.session_timeout
        }
    
    def validate_session(self) -> bool:
        """Valider la session actuelle"""
        if not self.is_authenticated():
            return False
        
        # Vérifier que l'utilisateur existe toujours et est actif
        employee = db_instance.get_employee(self.current_user.get('employee_id'))
        if not employee:
            print("⚠️ Utilisateur supprimé de la base de données")
            self.logout()
            return False
        
        if not employee.get('is_active'):
            print("⚠️ Compte utilisateur désactivé")
            self.logout()
            return False
        
        if not employee.get('is_login_active'):
            print("⚠️ Connexion désactivée pour cet utilisateur")
            self.logout()
            return False
        
        return True
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Changer le mot de passe de l'utilisateur courant"""
        if not self.current_user:
            return False, "Utilisateur non authentifié"
        
        employee_id = self.current_user.get('employee_id')
        
        # Validation de base
        if len(new_password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"
        
        if new_password == old_password:
            return False, "Le nouveau mot de passe doit être différent de l'ancien"
        
        # Vérifier l'ancien mot de passe
        if not db_instance.authenticate(employee_id, old_password):
            return False, "Ancien mot de passe incorrect"
        
        # Changer le mot de passe
        success, message = db_instance.change_password(employee_id, old_password, new_password)
        
        if success:
            # Mettre à jour l'utilisateur courant
            self.current_user = db_instance.get_employee(employee_id)
            print(f"✅ Mot de passe changé pour {employee_id}")
            return True, "Mot de passe changé avec succès"
        else:
            return False, message
    
    def reset_user_password(self, target_employee_id: str) -> Tuple[bool, str]:
        """Réinitialiser le mot de passe d'un utilisateur (RH/Admin seulement)"""
        if not self.can_manage_employees():
            return False, "Permission refusée: Seuls les administrateurs et RH peuvent réinitialiser les mots de passe"
        
        # Vérifier que l'utilisateur cible existe
        target_user = db_instance.get_employee(target_employee_id)
        if not target_user:
            return False, f"Employé {target_employee_id} non trouvé"
        
        # Réinitialiser le mot de passe
        success, message = db_instance.reset_password(target_employee_id)
        
        if success:
            print(f"✅ Mot de passe réinitialisé pour {target_employee_id} par {self.current_user.get('employee_id')}")
            return True, f"Mot de passe réinitialisé: {message}"
        else:
            return False, message
    
    def get_available_roles(self) -> List[Dict]:
        """Obtenir la liste des rôles disponibles"""
        return [
            {'id': 'admin', 'name': 'Administrateur', 'description': 'Accès complet au système'},
            {'id': 'hr', 'name': 'Ressources Humaines', 'description': 'Gestion des employés et congés'},
            {'id': 'manager', 'name': 'Manager', 'description': 'Gestion d\'équipe'},
            {'id': 'employee', 'name': 'Employé', 'description': 'Accès standard'}
        ]
    
    def check_user_exists(self, employee_id: str) -> bool:
        """Vérifier si un utilisateur existe"""
        try:
            employee = db_instance.get_employee(employee_id)
            return employee is not None
        except Exception:
            return False
    
    def get_user_role(self, employee_id: str) -> Optional[str]:
        """Obtenir le rôle d'un utilisateur"""
        try:
            employee = db_instance.get_employee(employee_id)
            return employee.get('role') if employee else None
        except Exception:
            return None
    
    # ============ MÉTHODES PRIVÉES ============
    
    def _get_role_display(self, role: str) -> str:
        """Obtenir le nom affichable d'un rôle"""
        role_map = {
            'admin': 'Administrateur',
            'hr': 'Ressources Humaines',
            'manager': 'Manager',
            'employee': 'Employé'
        }
        return role_map.get(role.lower(), role.capitalize())
    
    def _format_duration(self, seconds: float) -> str:
        """Formater une durée en secondes en texte lisible"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def _log_login_success(self, employee_id: str):
        """Journaliser une connexion réussie"""
        try:
            db_instance.cursor.execute('''
                INSERT INTO audit_log (table_name, record_id, action, new_values, changed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', ('auth', employee_id, 'LOGIN_SUCCESS', 'Connexion réussie', datetime.now()))
            db_instance.conn.commit()
        except Exception as e:
            print(f"⚠️ Erreur journalisation connexion: {e}")
    
    def _log_login_failure(self, employee_id: str):
        """Journaliser un échec de connexion"""
        try:
            db_instance.cursor.execute('''
                INSERT INTO audit_log (table_name, record_id, action, new_values, changed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', ('auth', employee_id, 'LOGIN_FAILED', 'Échec connexion', datetime.now()))
            db_instance.conn.commit()
        except Exception as e:
            print(f"⚠️ Erreur journalisation échec: {e}")
    
    def _log_logout(self, employee_id: str):
        """Journaliser une déconnexion"""
        try:
            db_instance.cursor.execute('''
                INSERT INTO audit_log (table_name, record_id, action, new_values, changed_at)
                VALUES (?, ?, ?, ?, ?)
            ''', ('auth', employee_id, 'LOGOUT', 'Déconnexion', datetime.now()))
            db_instance.conn.commit()
        except Exception as e:
            print(f"⚠️ Erreur journalisation déconnexion: {e}")

# Instance globale
auth_manager = AuthManager()

# ============ DÉCORATEURS D'AUTHENTIFICATION ============

def require_auth(func):
    """Décorateur pour exiger une authentification"""
    def wrapper(*args, **kwargs):
        if not auth_manager.is_authenticated():
            from tkinter import messagebox
            messagebox.showerror(
                "Accès refusé",
                "Veuillez vous connecter pour accéder à cette fonctionnalité."
            )
            return None
        return func(*args, **kwargs)
    return wrapper

def require_role(required_role: str):
    """Décorateur pour exiger un rôle spécifique"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_manager.is_authenticated():
                from tkinter import messagebox
                messagebox.showerror(
                    "Accès refusé",
                    "Veuillez vous connecter pour accéder à cette fonctionnalité."
                )
                return None
            
            if not auth_manager.has_role(required_role):
                from tkinter import messagebox
                role_display = auth_manager._get_role_display(required_role)
                messagebox.showerror(
                    "Permission refusée",
                    f"Rôle {role_display} requis pour cette action.\n"
                    f"Votre rôle: {auth_manager.current_user.get('role', 'N/A')}"
                )
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(required_permission: str):
    """Décorateur pour exiger une permission spécifique"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_manager.is_authenticated():
                from tkinter import messagebox
                messagebox.showerror(
                    "Accès refusé",
                    "Veuillez vous connecter pour accéder à cette fonctionnalité."
                )
                return None
            
            if not auth_manager.has_permission(required_permission):
                from tkinter import messagebox
                messagebox.showerror(
                    "Permission refusée",
                    f"Permission '{required_permission}' requise pour cette action."
                )
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ============ FONCTIONS UTILITAIRES ============

def test_authentication():
    """Tester l'authentification de tous les comptes"""
    print("\n" + "="*70)
    print("🧪 TEST COMPLET D'AUTHENTIFICATION")
    print("="*70)
    
    test_accounts = [
        ('ADMIN001', 'Admin@2024', 'Administrateur'),
        ('RH001', 'Rh@2024', 'Ressources Humaines'),
        ('EMP24001', 'Password123', 'Employé')
    ]
    
    results = []
    
    for emp_id, password, expected_role in test_accounts:
        print(f"\n{'─'*50}")
        print(f"🔍 TEST: {emp_id} (Attendu: {expected_role})")
        print(f"{'─'*50}")
        
        # Créer une nouvelle instance pour chaque test
        test_auth = AuthManager()
        user = test_auth.login(emp_id, password)
        
        if user:
            actual_role = test_auth._get_role_display(user.get('role', ''))
            status = "✅" if actual_role == expected_role else "⚠️"
            
            results.append({
                'id': emp_id,
                'status': 'SUCCESS',
                'expected': expected_role,
                'actual': actual_role,
                'match': actual_role == expected_role,
                'user': user.get('first_name', '') + ' ' + user.get('last_name', '')
            })
            
            print(f"{status} Authentification RÉUSSIE")
            print(f"   👤 Utilisateur: {user.get('first_name', '')} {user.get('last_name', '')}")
            print(f"   🎭 Rôle obtenu: {actual_role}")
            print(f"   🎯 Rôle attendu: {expected_role}")
            print(f"   {'✅ Correspondance' if actual_role == expected_role else '❌ Non correspondance'}")
            
            # Tester les permissions
            permissions = test_auth.get_user_permissions()
            print(f"   🔑 Permissions ({len(permissions)}):")
            for perm in permissions[:5]:  # Afficher seulement les 5 premières
                print(f"      • {perm}")
            if len(permissions) > 5:
                print(f"      • ... et {len(permissions) - 5} autres")
            
        else:
            results.append({
                'id': emp_id,
                'status': 'FAILED',
                'expected': expected_role,
                'actual': 'N/A',
                'match': False,
                'user': 'N/A'
            })
            
            print(f"❌ Authentification ÉCHOUÉE")
            print(f"   Raison probable: ID ou mot de passe incorrect")
        
        test_auth.logout()
    
    # Résumé
    print(f"\n{'='*70}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*70}")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    match_count = sum(1 for r in results if r.get('match', False))
    
    print(f"Total tests: {len(results)}")
    print(f"Authentifications réussies: {success_count}/{len(results)}")
    print(f"Rôles correspondants: {match_count}/{success_count if success_count > 0 else 1}")
    
    for result in results:
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        match_icon = "✅" if result.get('match', False) else "❌"
        
        if result['status'] == 'SUCCESS':
            print(f"  {status_icon} {result['id']}: {result['user']} - {result['actual']} {match_icon}")
        else:
            print(f"  {status_icon} {result['id']}: ÉCHEC d'authentification")
    
    print(f"\n💡 CONSEILS:")
    print(f"  • Vérifiez que la base de données a été réinitialisée")
    print(f"  • Les mots de passe sont sensibles à la casse")
    print(f"  • ADMIN001: Admin@2024")
    print(f"  • RH001: Rh@2024 (R majuscule)")
    print(f"  • EMP24001: Password123")
    print(f"{'='*70}\n")
    
    return results

def get_login_help():
    """Obtenir de l'aide pour la connexion"""
    help_text = """
    🆘 AIDE À LA CONNEXION - CLINIK RH
    
    COMPTES PAR DÉFAUT:
    ═══════════════════
    1. Administrateur
       • ID: ADMIN001
       • Mot de passe: Admin@2024
       • Rôle: Administrateur système (accès complet)
    
    2. Ressources Humaines
       • ID: RH001
       • Mot de passe: Rh@2024
       • IMPORTANT: Le 'R' est en majuscule
       • Rôle: Gestion des employés et congés
    
    3. Employé
       • ID: EMP24001
       • Mot de passe: Password123
       • Rôle: Employé standard
    
    PROBLÈMES COURANTS:
    ═══════════════════
    • Mot de passe incorrect: Vérifiez la casse (majuscules/minuscules)
    • Compte non trouvé: La base de données doit être réinitialisée
    • Erreur système: Vérifiez les logs dans le terminal
    
    RÉINITIALISATION:
    ════════════════
    Pour réinitialiser complètement:
    1. Supprimez le fichier: data/database/clinik_enterprise.db
    2. Redémarrez l'application
    3. Les comptes seront recréés automatiquement
    
    SUPPORT:
    ═══════
    • Consultez les logs dans le terminal pour plus de détails
    • Vérifiez que tous les modules sont installés
    • Assurez-vous d'avoir les permissions d'écriture
    """
    
    return help_text

# ============ INITIALISATION ============

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔧 INITIALISATION DU SYSTÈME D'AUTHENTIFICATION")
    print("="*70)
    
    # Tester l'authentification
    test_results = test_authentication()
    
    # Afficher l'aide
    print(get_login_help())
    
    # Vérifier la connexion à la base de données
    try:
        test_user = db_instance.get_employee("ADMIN001")
        if test_user:
            print("✅ Connexion à la base de données: OK")
        else:
            print("⚠️  Base de données: ADMIN001 non trouvé")
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")