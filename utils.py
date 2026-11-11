"""Utilitaires pour l'application CLINIK RH - VERSION FINALE
"""
import os
import json
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clinik_rh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration de l'application"""
    
    # Chemins
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "database" / "clinik_enterprise.db"
    BACKUP_DIR = DATA_DIR / "backups"
    EXPORT_DIR = DATA_DIR / "exports"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # Paramètres de l'application
    APP_NAME = "CLINIK RH Enterprise"
    APP_VERSION = "1.0.0"
    COMPANY_NAME = "CLINIK Corporation"
    
    # Configuration des congés
    LEAVE_TYPES = {
        'annual': {'name': 'Congé Annuel', 'days': 30, 'color': '#2A8C55'},
        'sick': {'name': 'Congé Maladie', 'days': 30, 'color': '#E74C3C'},
        'maternity': {'name': 'Congé Maternité', 'days': 98, 'color': '#9B59B6'},
        'paternity': {'name': 'Congé Paternité', 'days': 15, 'color': '#3498DB'},
        'training': {'name': 'Congé Formation', 'days': 10, 'color': '#F39C12'},
        'exceptional': {'name': 'Congé Exceptionnel', 'days': 5, 'color': '#1ABC9C'}
    }
    
    # Rôles et permissions
    ROLES = {
        'admin': ['all'],
        'hr': [
            'manage_employees', 'view_employees', 'edit_employees',
            'approve_leaves', 'view_leaves', 'export_data',
            'view_reports', 'manage_departments'
        ],
        'manager': [
            'view_team', 'approve_team_leaves', 'view_reports'
        ],
        'employee': [
            'view_own_profile', 'request_leave', 'view_own_leaves',
            'view_own_documents'
        ]
    }
    
    # Paramètres de l'interface
    THEME = "dark"  # "light", "dark", "system"
    PRIMARY_COLOR = "#2A8C55"
    SECONDARY_COLOR = "#3498DB"
    SUCCESS_COLOR = "#27AE60"
    WARNING_COLOR = "#F39C12"
    DANGER_COLOR = "#E74C3C"
    INFO_COLOR = "#17A2B8"
    
    # Paramètres de sécurité
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT = 3600  # 1 heure en secondes
    
    @classmethod
    def setup_directories(cls):
        """Créer les répertoires nécessaires"""
        directories = [
            cls.DATA_DIR,
            cls.DATA_DIR / "database",
            cls.BACKUP_DIR,
            cls.EXPORT_DIR,
            cls.ASSETS_DIR / "icons",
            cls.ASSETS_DIR / "images"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Répertoires configurés")

class DateUtils:
    """Utilitaires pour la manipulation des dates"""
    
    @staticmethod
    def format_date(date_obj, format_str="%d/%m/%Y"):
        """Formater une date"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
            except ValueError:
                return date_obj
        elif isinstance(date_obj, date):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        return date_obj.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str, format_str="%Y-%m-%d"):
        """Parser une chaîne en date"""
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            return None
    
    @staticmethod
    def calculate_working_days(start_date, end_date):
        """Calculer le nombre de jours ouvrables entre deux dates"""
        if not start_date or not end_date:
            return 0
        
        if isinstance(start_date, str):
            start_date = DateUtils.parse_date(start_date)
        if isinstance(end_date, str):
            end_date = DateUtils.parse_date(end_date)
        
        if not start_date or not end_date or start_date > end_date:
            return 0
        
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Lundi à vendredi sont des jours ouvrables
            if current_date.weekday() < 5:
                working_days += 1
            current_date += timedelta(days=1)
        
        return working_days
    
    @staticmethod
    def get_current_year():
        """Obtenir l'année en cours"""
        return datetime.now().year
    
    @staticmethod
    def get_fiscal_year(date_obj=None):
        """Obtenir l'année fiscale (du 1er juillet au 30 juin)"""
        if date_obj is None:
            date_obj = date.today()
        
        if date_obj.month >= 7:
            return date_obj.year
        else:
            return date_obj.year - 1
    
    @staticmethod
    def get_date_range_last_month():
        """Obtenir la période du mois dernier"""
        today = date.today()
        first_day_last_month = date(today.year, today.month - 1, 1) if today.month > 1 else date(today.year - 1, 12, 1)
        
        if today.month == 1:
            last_day_last_month = date(today.year - 1, 12, 31)
        else:
            last_day_last_month = date(today.year, today.month, 1) - timedelta(days=1)
        
        return first_day_last_month, last_day_last_month

class FileUtils:
    """Utilitaires pour la gestion des fichiers"""
    
    @staticmethod
    def save_json(data, filepath):
        """Sauvegarder des données en JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde JSON: {e}")
            return False
    
    @staticmethod
    def load_json(filepath):
        """Charger des données depuis JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Erreur chargement JSON: {e}")
            return {}
    
    @staticmethod
    def get_file_size(filepath):
        """Obtenir la taille d'un fichier en octets"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    @staticmethod
    def get_file_extension(filename):
        """Obtenir l'extension d'un fichier"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_allowed_file(filename, allowed_extensions=None):
        """Vérifier si un fichier a une extension autorisée"""
        if allowed_extensions is None:
            allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
        
        ext = FileUtils.get_file_extension(filename)
        return ext in allowed_extensions

class ValidationUtils:
    """Utilitaires de validation"""
    
    @staticmethod
    def validate_email(email):
        """Valider un email"""
        if not email:
            return True
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """Valider un numéro de téléphone"""
        if not phone:
            return True
        import re
        # Supprimer tous les caractères non numériques sauf +
        cleaned = re.sub(r'[^\d+]', '', phone)
        return 8 <= len(cleaned) <= 15
    
    @staticmethod
    def validate_cin(cin):
        """Valider un numéro CIN"""
        if not cin:
            return True
        import re
        pattern = r'^[A-Z]{1,2}\d{5,6}$'
        return bool(re.match(pattern, cin.upper()))
    
    @staticmethod
    def validate_password(password):
        """Valider un mot de passe"""
        if len(password) < Config.PASSWORD_MIN_LENGTH:
            return False, f"Le mot de passe doit contenir au moins {Config.PASSWORD_MIN_LENGTH} caractères"
        
        # Vérifier la complexité
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Le mot de passe doit contenir des majuscules, minuscules et chiffres"
        
        return True, "Mot de passe valide"
    
    @staticmethod
    def validate_iban(iban):
        """Valider un IBAN"""
        if not iban:
            return True
        import re
        pattern = r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'
        return bool(re.match(pattern, iban.replace(' ', '').upper()))

class ExportUtils:
    """Utilitaires pour l'export de données"""
    
    @staticmethod
    def export_to_excel(data, filename, sheet_name="Données"):
        """Exporter des données vers Excel"""
        try:
            import pandas as pd
            
            # S'assurer que le répertoire d'export existe
            export_path = Config.EXPORT_DIR / filename
            Config.EXPORT_DIR.mkdir(exist_ok=True)
            
            # Convertir en DataFrame
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
            else:
                logger.warning("Aucune donnée à exporter")
                return None
            
            # Sauvegarder
            df.to_excel(export_path, sheet_name=sheet_name, index=False)
            logger.info(f"Données exportées vers {export_path}")
            return str(export_path)
            
        except ImportError:
            logger.error("Pandas non installé pour l'export Excel")
            return None
        except Exception as e:
            logger.error(f"Erreur export Excel: {e}")
            return None
    
    @staticmethod
    def export_to_csv(data, filename):
        """Exporter des données vers CSV"""
        try:
            import pandas as pd
            
            export_path = Config.EXPORT_DIR / filename
            Config.EXPORT_DIR.mkdir(exist_ok=True)
            
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
            else:
                logger.warning("Aucune donnée à exporter")
                return None
            
            df.to_csv(export_path, index=False, encoding='utf-8-sig')
            logger.info(f"Données exportées vers {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Erreur export CSV: {e}")
            return None
    
    @staticmethod
    def generate_pdf_report(data, filename, title="Rapport"):
        """Générer un rapport PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            export_path = Config.EXPORT_DIR / filename
            Config.EXPORT_DIR.mkdir(exist_ok=True)
            
            doc = SimpleDocTemplate(str(export_path), pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Titre
            title_style = styles['Heading1']
            title_style.textColor = colors.HexColor(Config.PRIMARY_COLOR)
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 20))
            
            # Date de génération
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            elements.append(Paragraph(f"Généré le: {date_str}", styles['Normal']))
            elements.append(Spacer(1, 30))
            
            # Tableau
            if data and len(data) > 0:
                table_data = [list(data[0].keys())]  # En-têtes
                for row in data:
                    table_data.append([str(value) for value in row.values()])
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(Config.PRIMARY_COLOR)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('PADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(table)
            
            # Générer le PDF
            doc.build(elements)
            logger.info(f"Rapport PDF généré: {export_path}")
            return str(export_path)
            
        except ImportError:
            logger.error("ReportLab non installé pour l'export PDF")
            return None
        except Exception as e:
            logger.error(f"Erreur génération PDF: {e}")
            return None

class SecurityUtils:
    """Utilitaires de sécurité"""
    
    @staticmethod
    def generate_password_hash(password, salt=None):
        """Générer un hash sécurisé pour un mot de passe"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    @staticmethod
    def verify_password(password, password_hash, salt):
        """Vérifier un mot de passe"""
        test_hash, _ = SecurityUtils.generate_password_hash(password, salt)
        return test_hash == password_hash
    
    @staticmethod
    def generate_api_key():
        """Générer une clé API sécurisée"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_session_token():
        """Générer un token de session"""
        return secrets.token_hex(32)
    
    @staticmethod
    def sanitize_input(input_str):
        """Nettoyer une chaîne d'entrée"""
        import html
        if not input_str:
            return ""
        
        # Échapper les caractères HTML
        sanitized = html.escape(input_str)
        # Supprimer les scripts potentiels
        sanitized = sanitized.replace("<script>", "").replace("</script>", "")
        return sanitized.strip()

class BackupUtils:
    """Utilitaires de sauvegarde"""
    
    @staticmethod
    def create_backup(backup_type="full"):
        """Créer une sauvegarde"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{backup_type}_{timestamp}.db"
            backup_path = Config.BACKUP_DIR / backup_filename
            
            # Créer une copie de la base de données
            shutil.copy2(Config.DB_PATH, backup_path)
            
            logger.info(f"Sauvegarde créée: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Erreur création sauvegarde: {e}")
            return None
    
    @staticmethod
    def get_backup_list():
        """Obtenir la liste des sauvegardes disponibles"""
        backups = []
        try:
            for file in Config.BACKUP_DIR.glob("backup_*.db"):
                stats = file.stat()
                backups.append({
                    'filename': file.name,
                    'path': str(file),
                    'size': stats.st_size,
                    'created': datetime.fromtimestamp(stats.st_ctime)
                })
            
            # Trier par date de création (plus récent d'abord)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Erreur liste sauvegardes: {e}")
            return []
    
    @staticmethod
    def restore_backup(backup_path):
        """Restaurer une sauvegarde"""
        try:
            import shutil
            
            # Créer une sauvegarde avant restauration
            BackupUtils.create_backup("pre_restore")
            
            # Restaurer
            shutil.copy2(backup_path, Config.DB_PATH)
            
            logger.info(f"Base de données restaurée depuis: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur restauration: {e}")
            return False

# Initialisation
Config.setup_directories()