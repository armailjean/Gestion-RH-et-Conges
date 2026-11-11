"""
Application principale CLINIK RH Enterprise - VERSION AVEC CYCLE LOGIN/LOGOUT
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from database import Database
from auth import auth_manager
from ui.login_ui import LoginWindow
from ui.dashboard_ui import DashboardWindow

class ClinikRHApp:
    """Application principale CLINIK RH avec gestion du cycle login"""
    
    def __init__(self):
        # Configuration de CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Vérifier/Créer les répertoires
        self._setup_directories()
        
        # Références aux fenêtres
        self.login_window = None
        self.dashboard_window = None
        
        print("""
        ╔══════════════════════════════════════════════════════╗
        ║             CLINIK RH ENTERPRISE v1.0.0              ║
        ║        Système de Gestion des Ressources Humaines    ║
        ╚══════════════════════════════════════════════════════╝
        
        🔧 Initialisation de la base de données...
        """)
    
    def _setup_directories(self):
        """Configurer les répertoires nécessaires"""
        directories = [
            "data/database",
            "data/backups",
            "data/exports",
            "assets/icons",
            "assets/images"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Démarrer l'application avec l'écran de login"""
        self.show_login()
    
    def show_login(self):
        """Afficher l'écran de connexion"""
        # Fermer le dashboard si ouvert
        if self.dashboard_window and hasattr(self.dashboard_window, 'window') and self.dashboard_window.window:
            try:
                self.dashboard_window.window.destroy()
            except:
                pass
        
        # Créer la fenêtre de login
        self.login_window = LoginWindow(self.on_login_success)
        self.login_window.run()
    
    def on_login_success(self, user_data):
        """Callback après connexion réussie"""
        print(f"\n✅ Connexion réussie: {user_data['first_name']} {user_data['last_name']}")
        print(f"👤 Rôle: {user_data['role']}")
        print(f"🏢 Département: {user_data.get('department_name', 'N/A')}")
        
        # Fermer la fenêtre de login
        if self.login_window and hasattr(self.login_window, 'window') and self.login_window.window:
            try:
                self.login_window.window.destroy()
            except:
                pass
        
        # Afficher le tableau de bord
        self.show_dashboard(user_data)
    
    def show_dashboard(self, user_data):
        """Afficher le tableau de bord"""
        # Créer le dashboard avec callback pour le logout
        self.dashboard_window = DashboardWindow(
            user_data=user_data,
            on_logout_callback=self.on_logout
        )
        self.dashboard_window.run()
    
    def on_logout(self):
        """Callback après déconnexion - Retour au login"""
        print("\n🔒 Déconnexion demandée - Retour à l'écran de login")
        
        # Nettoyer l'authentification
        auth_manager.logout()
        
        # Fermer le dashboard
        if self.dashboard_window and hasattr(self.dashboard_window, 'window') and self.dashboard_window.window:
            try:
                self.dashboard_window.window.destroy()
            except:
                pass
        
        # Petit délai avant de revenir au login
        import time
        time.sleep(0.5)
        
        # Revenir au login
        self.show_login()
    
    def cleanup(self):
        """Nettoyage à la fermeture de l'application"""
        print("\n🧹 Fermeture de l'application...")
        from database import db_instance
        db_instance.close()
        print("✅ Base de données fermée")
        print("👋 À bientôt sur CLINIK RH!")

def main():
    """Fonction principale"""
    try:
        app = ClinikRHApp()
        app.start()
    except KeyboardInterrupt:
        print("\n\n❌ Application interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'app' in locals():
            app.cleanup()

if __name__ == "__main__":
    main()