"""
Base de données avancée pour CLINIK RH - VERSION FINALE
"""
import sqlite3
import os
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import hashlib
import secrets
import random
import string

class Database:
    """Classe de gestion de la base de données"""
    
    def __init__(self, db_path: str = "data/database/clinik_enterprise.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        
        # Créer le répertoire si nécessaire
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialiser la base de données
        self.connect()
        self.initialize_database()
    
    def connect(self) -> bool:
        """Établir la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Pour obtenir des dictionnaires
            self.cursor = self.conn.cursor()
            
            # Activer les clés étrangères
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            print(f"✅ Base de données connectée: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion DB: {e}")
            return False
    
    def db_exists(self) -> bool:
        """Vérifier si la base de données existe"""
        return self.db_path.exists()
    
    def initialize_database(self):
        """Initialiser les tables de la base de données"""
        try:
            # Créer les tables
            self._create_tables()
            
            # Vérifier si des données existent déjà
            self.cursor.execute("SELECT COUNT(*) FROM employees")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Créer les données de test
                self._create_test_data()
                print("✅ Données de test créées")
            else:
                print(f"⚠️ {count} employés déjà présents dans la base")
            
            print("✅ Base de données initialisée")
            
        except Exception as e:
            print(f"❌ Erreur initialisation DB: {e}")
            raise
    
    def _create_tables(self):
        """Créer toutes les tables nécessaires"""
        
        # Table des départements
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                manager_id TEXT,
                budget REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des postes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                department_id INTEGER,
                grade TEXT,
                salary_min REAL DEFAULT 0.0,
                salary_max REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')
        
        # Table des employés
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                last_name TEXT NOT NULL,
                first_name TEXT NOT NULL,
                gender TEXT,
                birth_date DATE,
                personal_email TEXT,
                work_email TEXT UNIQUE,
                personal_phone TEXT,
                work_phone TEXT,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                cin TEXT UNIQUE,
                nationality TEXT DEFAULT 'Marocaine',
                hire_date DATE NOT NULL,
                contract_type TEXT,
                contract_end DATE,
                position_id INTEGER,
                department_id INTEGER,
                salary REAL,
                marital_status TEXT,
                children_count INTEGER DEFAULT 0,
                emergency_name TEXT,
                emergency_phone TEXT,
                emergency_relation TEXT,
                bank_name TEXT,
                iban TEXT,
                role TEXT DEFAULT 'employee' CHECK(role IN ('admin', 'hr', 'manager', 'employee')),
                is_active INTEGER DEFAULT 1,
                is_login_active INTEGER DEFAULT 1,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (position_id) REFERENCES positions(id),
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')
        
        # Table des demandes de congé
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT UNIQUE NOT NULL,
                employee_id TEXT NOT NULL,
                leave_type TEXT NOT NULL CHECK(leave_type IN ('annual', 'sick', 'maternity', 'paternity', 'training', 'exceptional')),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                total_days INTEGER NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')),
                approved_by TEXT,
                approval_date TIMESTAMP,
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
                FOREIGN KEY (approved_by) REFERENCES employees(employee_id)
            )
        ''')
        
        # Table des soldes de congés
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                annual_total INTEGER DEFAULT 30,
                annual_taken INTEGER DEFAULT 0,
                annual_remaining INTEGER GENERATED ALWAYS AS (annual_total - annual_taken) VIRTUAL,
                sick_total INTEGER DEFAULT 30,
                sick_taken INTEGER DEFAULT 0,
                sick_remaining INTEGER GENERATED ALWAYS AS (sick_total - sick_taken) VIRTUAL,
                maternity_total INTEGER DEFAULT 98,
                maternity_taken INTEGER DEFAULT 0,
                training_total INTEGER DEFAULT 10,
                training_taken INTEGER DEFAULT 0,
                exceptional_total INTEGER DEFAULT 5,
                exceptional_taken INTEGER DEFAULT 0,
                fiscal_year INTEGER DEFAULT (strftime('%Y', date('now', 'start of year', '+6 months'))),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        ''')
        
        # Journal d'audit
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                changed_by TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (changed_by) REFERENCES employees(employee_id)
            )
        ''')
        
        self.conn.commit()
        print("✅ Tables créées avec succès")
    
    def _create_test_data(self):
        """Créer les données de test"""
        
        print("📝 Création des données de test...")
        
        # 1. Créer les départements
        departments = [
            ('IT', 'Technologies de l\'Information', 'Service informatique', None, 500000.0),
            ('RH', 'Ressources Humaines', 'Gestion du personnel', None, 300000.0),
            ('FIN', 'Finances', 'Service financier', None, 800000.0),
            ('PROD', 'Production', 'Service de production', None, 1200000.0),
            ('COM', 'Commercial', 'Service commercial', None, 400000.0)
        ]
        
        dept_ids = {}
        for code, name, desc, manager, budget in departments:
            self.cursor.execute('''
                INSERT INTO departments (code, name, description, budget)
                VALUES (?, ?, ?, ?)
            ''', (code, name, desc, budget))
            dept_ids[code] = self.cursor.lastrowid
        
        # 2. Créer les postes
        positions = [
            ('DIR-IT', 'Directeur IT', 'Direction informatique', 'IT', 'A', 25000, 40000),
            ('DEV-SEN', 'Développeur Senior', 'Développement logiciel', 'IT', 'B', 15000, 25000),
            ('DEV-JUN', 'Développeur Junior', 'Développement junior', 'IT', 'C', 8000, 15000),
            ('DIR-RH', 'Directeur RH', 'Direction ressources humaines', 'RH', 'A', 20000, 35000),
            ('RH-MAN', 'Manager RH', 'Gestion RH', 'RH', 'B', 12000, 20000),
            ('COMPTA', 'Comptable', 'Gestion comptable', 'FIN', 'B', 10000, 18000),
            ('PROD-MAN', 'Manager Production', 'Gestion production', 'PROD', 'B', 13000, 22000),
            ('TECH', 'Technicien', 'Technicien de production', 'PROD', 'C', 7000, 12000),
            ('COMM', 'Commercial', 'Vente et relation client', 'COM', 'B', 9000, 16000)
        ]
        
        pos_ids = {}
        for code, title, desc, dept_code, grade, min_sal, max_sal in positions:
            dept_id = dept_ids.get(dept_code)
            if dept_id:
                self.cursor.execute('''
                    INSERT INTO positions (code, title, description, department_id, grade, salary_min, salary_max)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (code, title, desc, dept_id, grade, min_sal, max_sal))
                pos_ids[code] = self.cursor.lastrowid
        
        # 3. Fonction pour hasher les mots de passe
        def hash_password(password):
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash, salt
        
        # 4. Créer les employés de test
        test_employees = [
            # Administrateur
            ('ADMIN001', 'Admin', 'System', 'Homme', '1980-01-01', 
             'admin.perso@example.com', 'admin@clinik.com', '0600000001', '0500000001',
             '123 Rue Admin', 'Casablanca', '20000', 'AB123456', 'Admin@2024',
             '2020-01-01', 'CDI', None, 'DIR-IT', 'IT', 35000.0, 'Marié(e)', 2,
             'Contact Admin', '0600000002', 'Conjoint', 'BMCE', 'MA6401234567890123456789012',
             'admin', hash_password('Admin@2024')),
            
            # Ressources Humaines
            ('RH001', 'Dupont', 'Marie', 'Femme', '1985-05-15',
             'marie.dupont.perso@example.com', 'marie.dupont@clinik.com', '0600000011', '0500000011',
             '456 Avenue RH', 'Casablanca', '20000', 'CD789012', 'Rh@2024',
             '2021-03-15', 'CDI', None, 'DIR-RH', 'RH', 28000.0, 'Marié(e)', 1,
             'Jean Dupont', '0600000012', 'Conjoint', 'CIH', 'MA6455501234567890123456789',
             'hr', hash_password('Rh@2024')),
            
            # Employé test 1
            ('EMP24001', 'Martin', 'Jean', 'Homme', '1990-08-20',
             'jean.martin.perso@example.com', 'jean.martin@clinik.com', '0600000021', '0500000021',
             '789 Rue Employé', 'Casablanca', '20000', 'EF345678', 'Password123',
             '2024-01-15', 'CDI', None, 'DEV-JUN', 'IT', 12000.0, 'Célibataire', 0,
             'Parents Martin', '0600000022', 'Parents', 'Attijariwafa', 'MA6411112222333344445555666',
             'employee', hash_password('Password123')),
            
            # Employé test 2
            ('EMP24002', 'Bernard', 'Sophie', 'Femme', '1992-11-30',
             'sophie.bernard.perso@example.com', 'sophie.bernard@clinik.com', '0600000031', '0500000031',
             '321 Boulevard Test', 'Casablanca', '20000', 'GH901234', 'Password456',
             '2024-02-01', 'CDD', '2025-02-01', 'COMPTA', 'FIN', 14000.0, 'Célibataire', 0,
             'Paul Bernard', '0600000032', 'Frère', 'BMCI', 'MA6422223333444455556666777',
             'employee', hash_password('Password456')),
            
            # Manager test
            ('MGR001', 'Dubois', 'Pierre', 'Homme', '1978-03-10',
             'pierre.dubois.perso@example.com', 'pierre.dubois@clinik.com', '0600000041', '0500000041',
             '654 Avenue Manager', 'Casablanca', '20000', 'IJ567890', 'Manager@2024',
             '2019-06-01', 'CDI', None, 'PROD-MAN', 'PROD', 18000.0, 'Marié(e)', 3,
             'Julie Dubois', '0600000042', 'Conjoint', 'SGMB', 'MA6433334444555566667777888',
             'manager', hash_password('Manager@2024'))
        ]
        
        for emp in test_employees:
            (emp_id, last_name, first_name, gender, birth_date, 
             personal_email, work_email, personal_phone, work_phone,
             address, city, postal_code, cin, password,
             hire_date, contract_type, contract_end, pos_code, dept_code, salary,
             marital_status, children_count, emergency_name, emergency_phone, emergency_relation,
             bank_name, iban, role, (password_hash, password_salt)) = emp
            
            position_id = pos_ids.get(pos_code)
            department_id = dept_ids.get(dept_code)
            
            if position_id and department_id:
                self.cursor.execute('''
                    INSERT INTO employees (
                        employee_id, last_name, first_name, gender, birth_date,
                        personal_email, work_email, personal_phone, work_phone,
                        address, city, postal_code, cin,
                        hire_date, contract_type, contract_end, position_id, department_id, salary,
                        marital_status, children_count, emergency_name, emergency_phone, emergency_relation,
                        bank_name, iban, role, password_hash, password_salt
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    emp_id, last_name, first_name, gender, birth_date,
                    personal_email, work_email, personal_phone, work_phone,
                    address, city, postal_code, cin,
                    hire_date, contract_type, contract_end, position_id, department_id, salary,
                    marital_status, children_count, emergency_name, emergency_phone, emergency_relation,
                    bank_name, iban, role, password_hash, password_salt
                ))
        
        # 5. Créer les soldes de congés
        for emp_id in ['ADMIN001', 'RH001', 'EMP24001', 'EMP24002', 'MGR001']:
            self.cursor.execute('''
                INSERT OR IGNORE INTO leave_balances (employee_id)
                VALUES (?)
            ''', (emp_id,))
        
        self.conn.commit()
        print(f"✅ {len(test_employees)} employés de test créés")
        print("✅ Données de test initialisées avec succès")
    
    def authenticate(self, employee_id: str, password: str) -> Optional[Dict]:
        """Authentifier un utilisateur"""
        try:
            print(f"\n[Auth] Tentative pour: {employee_id}")
            
            # Récupérer l'utilisateur
            self.cursor.execute('''
                SELECT e.*, d.name as department_name, p.title as position_title
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE e.employee_id = ? AND e.is_active = 1 AND e.is_login_active = 1
            ''', (employee_id,))
            
            row = self.cursor.fetchone()
            
            if not row:
                print(f"[Auth] Employé {employee_id} non trouvé ou inactif")
                return None
            
            employee = dict(row)
            
            # Vérifier le mot de passe
            stored_hash = employee['password_hash']
            salt = employee['password_salt']
            
            # Hasher le mot de passe fourni avec le même salt
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            if test_hash == stored_hash:
                # Mettre à jour la dernière connexion
                self.cursor.execute('''
                    UPDATE employees 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE employee_id = ?
                ''', (employee_id,))
                self.conn.commit()
                
                # Formater la réponse
                employee.pop('password_hash', None)
                employee.pop('password_salt', None)
                
                print(f"[Auth] ✅ Connexion réussie pour {employee_id}")
                return employee
            else:
                print(f"[Auth] ❌ Mot de passe incorrect pour {employee_id}")
                return None
                
        except Exception as e:
            print(f"[Auth] ❌ Erreur authentification: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Récupérer un employé par son ID"""
        try:
            self.cursor.execute('''
                SELECT e.*, d.name as department_name, p.title as position_title,
                       p.grade as position_grade
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE e.employee_id = ?
            ''', (employee_id,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Erreur get_employee: {e}")
            return None
    
    def get_all_employees(self, active_only: bool = False, department_id: Optional[int] = None) -> List[Dict]:
        """Récupérer tous les employés"""
        try:
            query = '''
                SELECT e.*, d.name as department_name, p.title as position_title
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id
                LEFT JOIN positions p ON e.position_id = p.id
                WHERE 1=1
            '''
            params = []
            
            if active_only:
                query += " AND e.is_active = 1"
            
            if department_id:
                query += " AND e.department_id = ?"
                params.append(department_id)
            
            query += " ORDER BY e.last_name, e.first_name"
            
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Erreur get_all_employees: {e}")
            return []
    
    def create_employee(self, employee_data: Dict) -> Tuple[bool, str]:
        """Créer un nouvel employé"""
        try:
            # Générer un ID employé si non fourni
            if 'employee_id' not in employee_data or not employee_data['employee_id']:
                employee_data['employee_id'] = self._generate_employee_id()
            
            # Hasher le mot de passe
            password = employee_data.pop('password', 'Password123')
            password_hash, password_salt = self._hash_password(password)
            
            employee_data['password_hash'] = password_hash
            employee_data['password_salt'] = password_salt
            
            # Construire la requête
            columns = ', '.join(employee_data.keys())
            placeholders = ', '.join(['?' for _ in employee_data])
            values = list(employee_data.values())
            
            query = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            # Créer le solde de congés
            employee_id = employee_data['employee_id']
            self.cursor.execute('''
                INSERT OR IGNORE INTO leave_balances (employee_id)
                VALUES (?)
            ''', (employee_id,))
            self.conn.commit()
            
            return True, f"Employé {employee_id} créé avec succès"
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                return False, "ID employé ou email déjà existant"
            return False, f"Erreur d'intégrité: {e}"
        except Exception as e:
            return False, f"Erreur création employé: {e}"
    
    def update_employee(self, employee_id: str, updates: Dict) -> Tuple[bool, str]:
        """Mettre à jour un employé"""
        try:
            if not updates:
                return False, "Aucune mise à jour fournie"
            
            # Ajouter la date de mise à jour
            updates['updated_at'] = datetime.now().isoformat()
            
            # Préparer la requête
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            
            query = f"UPDATE employees SET {set_clause} WHERE employee_id = ?"
            values = list(updates.values()) + [employee_id]
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return True, f"Employé {employee_id} mis à jour avec succès"
            else:
                return False, f"Employé {employee_id} non trouvé"
                
        except Exception as e:
            return False, f"Erreur mise à jour employé: {e}"
    
    def create_leave_request(self, request_data: Dict) -> Tuple[bool, str]:
        """Créer une demande de congé"""
        try:
            # Générer un numéro de demande
            request_number = self._generate_request_number()
            request_data['request_number'] = request_number
            
            # Construire la requête
            columns = ', '.join(request_data.keys())
            placeholders = ', '.join(['?' for _ in request_data])
            values = list(request_data.values())
            
            query = f"INSERT INTO leave_requests ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            return True, request_number
            
        except Exception as e:
            return False, f"Erreur création demande: {e}"
    
    def get_leave_requests(self, status: Optional[str] = None) -> List[Dict]:
        """Récupérer les demandes de congé"""
        try:
            query = '''
                SELECT lr.*, e.last_name, e.first_name, e.work_email
                FROM leave_requests lr
                JOIN employees e ON lr.employee_id = e.employee_id
                WHERE 1=1
            '''
            params = []
            
            if status:
                query += " AND lr.status = ?"
                params.append(status)
            
            query += " ORDER BY lr.created_at DESC"
            
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Erreur get_leave_requests: {e}")
            return []
    
    def get_leave_balance(self, employee_id: str) -> Dict:
        """Obtenir le solde de congés d'un employé"""
        try:
            self.cursor.execute('''
                SELECT * FROM leave_balances 
                WHERE employee_id = ?
            ''', (employee_id,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else {
                'annual_total': 30, 'annual_taken': 0, 'annual_remaining': 30,
                'sick_total': 30, 'sick_taken': 0, 'sick_remaining': 30,
                'maternity_total': 98, 'maternity_taken': 0,
                'training_total': 10, 'training_taken': 0,
                'exceptional_total': 5, 'exceptional_taken': 0
            }
        except Exception as e:
            print(f"Erreur get_leave_balance: {e}")
            return {}
    
    def get_dashboard_stats(self) -> Dict:
        """Obtenir les statistiques pour le tableau de bord"""
        try:
            stats = {}
            
            # Effectif total
            self.cursor.execute("SELECT COUNT(*) FROM employees WHERE is_active = 1")
            stats['total_employees'] = self.cursor.fetchone()[0]
            
            # Congés en attente
            self.cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'")
            stats['pending_leaves'] = self.cursor.fetchone()[0]
            
            # Employés par département
            self.cursor.execute('''
                SELECT d.name, COUNT(e.id) as count
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id AND e.is_active = 1
                WHERE d.is_active = 1
                GROUP BY d.id
                ORDER BY count DESC
            ''')
            stats['by_department'] = [dict(row) for row in self.cursor.fetchall()]
            
            # Nouveaux ce mois-ci
            current_month = date.today().replace(day=1)
            self.cursor.execute('''
                SELECT COUNT(*) FROM employees 
                WHERE hire_date >= ? AND is_active = 1
            ''', (current_month.isoformat(),))
            stats['new_this_month'] = self.cursor.fetchone()[0]
            
            # Absents aujourd'hui (congés approuvés qui incluent aujourd'hui)
            today = date.today().isoformat()
            self.cursor.execute('''
                SELECT COUNT(DISTINCT lr.employee_id)
                FROM leave_requests lr
                WHERE lr.status = 'approved'
                AND lr.start_date <= ? 
                AND lr.end_date >= ?
            ''', (today, today))
            stats['absent_today'] = self.cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            print(f"Erreur get_dashboard_stats: {e}")
            return {}
    
    def change_password(self, employee_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Changer le mot de passe"""
        try:
            # Vérifier l'ancien mot de passe
            user = self.authenticate(employee_id, old_password)
            if not user:
                return False, "Ancien mot de passe incorrect"
            
            # Hasher le nouveau mot de passe
            password_hash, password_salt = self._hash_password(new_password)
            
            self.cursor.execute('''
                UPDATE employees 
                SET password_hash = ?, password_salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE employee_id = ?
            ''', (password_hash, password_salt, employee_id))
            
            self.conn.commit()
            return True, "Mot de passe changé avec succès"
            
        except Exception as e:
            return False, f"Erreur changement mot de passe: {e}"
    
    def reset_password(self, employee_id: str) -> Tuple[bool, str]:
        """Réinitialiser le mot de passe d'un employé"""
        try:
            # Vérifier que l'employé existe
            employee = self.get_employee(employee_id)
            if not employee:
                return False, f"Employé {employee_id} non trouvé"
            
            # Générer un nouveau mot de passe aléatoire
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Hasher et mettre à jour
            password_hash, password_salt = self._hash_password(new_password)
            
            self.cursor.execute('''
                UPDATE employees 
                SET password_hash = ?, password_salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE employee_id = ?
            ''', (password_hash, password_salt, employee_id))
            
            self.conn.commit()
            return True, new_password
            
        except Exception as e:
            return False, f"Erreur réinitialisation mot de passe: {e}"
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            print("✅ Connexion à la base de données fermée")
    
    # ============ MÉTHODES PRIVÉES ============
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """Hasher un mot de passe avec un salt aléatoire"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def _generate_employee_id(self) -> str:
        """Générer un ID employé unique"""
        while True:
            # Format: EMP + année + 3 chiffres aléatoires
            year = datetime.now().year
            random_part = ''.join(random.choices(string.digits, k=3))
            emp_id = f"EMP{year % 100:02d}{random_part}"
            
            # Vérifier si l'ID existe déjà
            self.cursor.execute("SELECT COUNT(*) FROM employees WHERE employee_id = ?", (emp_id,))
            if self.cursor.fetchone()[0] == 0:
                return emp_id
    
    def _generate_request_number(self) -> str:
        """Générer un numéro de demande unique"""
        while True:
            # Format: LV + date + 4 caractères aléatoires
            date_str = datetime.now().strftime("%y%m%d")
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            request_number = f"LV{date_str}{random_part}"
            
            # Vérifier si le numéro existe déjà
            self.cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE request_number = ?", (request_number,))
            if self.cursor.fetchone()[0] == 0:
                return request_number

# Instance globale de la base de données
db_instance = Database()
