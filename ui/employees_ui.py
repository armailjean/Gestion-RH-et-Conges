"""
Interface de gestion des employés - VERSION FINALE
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from datetime import datetime
from typing import List, Dict, Optional

from database import db_instance
from models import Employee
from utils import Config, ValidationUtils, ExportUtils
from ui.components import ModernTable, ModernCard, DatePicker

class EmployeesWindow:
    """Fenêtre de gestion des employés"""
    
    def __init__(self, master, user_role: str):
        self.master = master
        self.user_role = user_role
        self.current_employee = None
        self.employees = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame,
            text="👥 Gestion des Employés",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")
        
        # Bouton nouveau (seulement pour RH/Admin)
        if self.user_role in ['admin', 'hr']:
            ctk.CTkButton(
                title_frame,
                text="➕ Nouvel Employé",
                command=self.show_create_form,
                width=120,
                height=35,
                fg_color=Config.PRIMARY_COLOR
            ).pack(side="right", padx=(10, 0))
        
        # Barre de recherche et filtres
        self.create_filters()
        
        # Tableau des employés
        self.create_employees_table()
        
        # Charger les données
        self.load_employees()
    
    def create_filters(self):
        """Créer la barre de filtres"""
        filters_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        filters_frame.pack(fill="x", pady=(0, 20))
        
        # Recherche
        search_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 16)).pack(side="left", padx=(0, 10))
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Rechercher par nom, ID, email...",
            width=300
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_employees())
        
        # Filtre département
        dept_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        dept_frame.pack(side="right")
        
        ctk.CTkLabel(dept_frame, text="Département:", font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        
        # Charger les départements
        departments = self.get_departments()
        dept_options = ["Tous"] + [dept['name'] for dept in departments]
        
        self.dept_combo = ctk.CTkComboBox(
            dept_frame,
            values=dept_options,
            width=150,
            command=self.on_department_filter
        )
        self.dept_combo.pack(side="left")
        
        # Bouton réinitialiser
        ctk.CTkButton(
            dept_frame,
            text="↻",
            width=30,
            height=30,
            command=self.reset_filters,
            fg_color="transparent",
            hover_color=("gray80", "gray30")
        ).pack(side="left", padx=(10, 0))
    
    def create_employees_table(self):
        """Créer le tableau des employés"""
        columns = ["ID", "Nom", "Prénom", "Département", "Poste", "Date Embauche", "Statut", "Actions"]
        
        self.table = ModernTable(self.frame, columns, height=400)
        self.table.pack(fill="both", expand=True)
        
        # Lier le double-clic
        self.table.tree.bind("<Double-1>", self.on_employee_double_click)
    
    def get_departments(self) -> List[Dict]:
        """Récupérer la liste des départements"""
        try:
            db_instance.cursor.execute("SELECT id, name FROM departments WHERE is_active = 1 ORDER BY name")
            return [dict(row) for row in db_instance.cursor.fetchall()]
        except Exception as e:
            print(f"Erreur récupération départements: {e}")
            return []
    
    def load_employees(self, department_id: Optional[int] = None):
        """Charger les employés"""
        try:
            self.employees = db_instance.get_all_employees(
                active_only=True,
                department_id=department_id
            )
            self.display_employees(self.employees)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les employés: {e}")
    
    def display_employees(self, employees: List[Dict]):
        """Afficher les employés dans le tableau"""
        data = []
        for emp in employees:
            actions = "👁️"
            if self.user_role in ['admin', 'hr']:
                actions += " 📝"
            
            data.append([
                emp['employee_id'],
                emp['last_name'],
                emp['first_name'],
                emp.get('department_name', ''),
                emp.get('position_title', ''),
                emp.get('hire_date', ''),
                '🟢 Actif' if emp.get('is_active', False) else '🔴 Inactif',
                actions
            ])
        
        self.table.set_data(data)
    
    def filter_employees(self):
        """Filtrer les employés selon la recherche"""
        search_term = self.search_entry.get().lower()
        
        if not search_term:
            self.display_employees(self.employees)
            return
        
        filtered = []
        for emp in self.employees:
            if (search_term in emp.get('last_name', '').lower() or
                search_term in emp.get('first_name', '').lower() or
                search_term in emp.get('employee_id', '').lower() or
                search_term in emp.get('work_email', '').lower() or
                search_term in emp.get('department_name', '').lower()):
                filtered.append(emp)
        
        self.display_employees(filtered)
    
    def on_department_filter(self, choice):
        """Filtrer par département"""
        if choice == "Tous":
            self.load_employees()
        else:
            # Trouver l'ID du département
            departments = self.get_departments()
            dept_id = None
            for dept in departments:
                if dept['name'] == choice:
                    dept_id = dept['id']
                    break
            
            if dept_id:
                self.load_employees(dept_id)
    
    def reset_filters(self):
        """Réinitialiser tous les filtres"""
        self.search_entry.delete(0, tk.END)
        self.dept_combo.set("Tous")
        self.load_employees()
    
    def on_employee_double_click(self, event):
        """Gérer le double-clic sur un employé"""
        selection = self.table.tree.selection()
        if selection:
            item = self.table.tree.item(selection[0])
            employee_id = item['values'][0]
            self.show_employee_details(employee_id)
    
    def show_employee_details(self, employee_id: str):
        """Afficher les détails d'un employé"""
        try:
            employee = db_instance.get_employee(employee_id)
            if not employee:
                messagebox.showwarning("Erreur", "Employé non trouvé")
                return
            
            # Créer une fenêtre modale
            details_window = ctk.CTkToplevel(self.master)
            details_window.title(f"Détails Employé - {employee_id}")
            details_window.geometry("800x600")
            details_window.transient(self.master)
            details_window.grab_set()
            
            # Frame principal avec scroll
            main_frame = ctk.CTkScrollableFrame(details_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Titre
            ctk.CTkLabel(
                main_frame,
                text=f"👤 {employee['first_name']} {employee['last_name']}",
                font=("Segoe UI", 20, "bold")
            ).pack(pady=(0, 20))
            
            # Sections d'information
            self.create_employee_info_section(main_frame, employee)
            
            # Boutons d'action
            if self.user_role in ['admin', 'hr']:
                button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                button_frame.pack(fill="x", pady=20)
                
                ctk.CTkButton(
                    button_frame,
                    text="📝 Modifier",
                    command=lambda: self.edit_employee(employee_id),
                    width=100,
                    fg_color=Config.WARNING_COLOR
                ).pack(side="left", padx=5)
                
                ctk.CTkButton(
                    button_frame,
                    text="📊 Congés",
                    command=lambda: self.show_employee_leaves(employee_id),
                    width=100
                ).pack(side="left", padx=5)
                
                if employee.get('is_active', False):
                    ctk.CTkButton(
                        button_frame,
                        text="🔴 Désactiver",
                        command=lambda: self.toggle_employee_status(employee_id, False),
                        width=100,
                        fg_color=Config.DANGER_COLOR
                    ).pack(side="left", padx=5)
                else:
                    ctk.CTkButton(
                        button_frame,
                        text="🟢 Activer",
                        command=lambda: self.toggle_employee_status(employee_id, True),
                        width=100,
                        fg_color=Config.SUCCESS_COLOR
                    ).pack(side="left", padx=5)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher les détails: {e}")
    
    def create_employee_info_section(self, parent, employee: Dict):
        """Créer la section d'information de l'employé"""
        sections = [
            ("Informations Personnelles", [
                ("ID Employé", employee.get('employee_id', '')),
                ("CIN", employee.get('cin', 'Non renseigné')),
                ("Date Naissance", employee.get('birth_date', '')),
                ("Genre", employee.get('gender', '')),
                ("Situation Familiale", employee.get('marital_status', '')),
                ("Nombre d'Enfants", employee.get('children_count', 0))
            ]),
            
            ("Coordonnées", [
                ("Adresse", employee.get('address', '')),
                ("Ville", employee.get('city', '')),
                ("Code Postal", employee.get('postal_code', '')),
                ("Téléphone Personnel", employee.get('personal_phone', '')),
                ("Email Personnel", employee.get('personal_email', '')),
                ("Téléphone Professionnel", employee.get('work_phone', '')),
                ("Email Professionnel", employee.get('work_email', ''))
            ]),
            
            ("Informations Professionnelles", [
                ("Date d'Embauche", employee.get('hire_date', '')),
                ("Type de Contrat", employee.get('contract_type', '')),
                ("Date Fin Contrat", employee.get('contract_end', '')),
                ("Département", employee.get('department_name', '')),
                ("Poste", employee.get('position_title', '')),
                ("Grade", employee.get('position_grade', '')),
                ("Salaire Base", f"{employee.get('salary', 0):,.2f} MAD" if employee.get('salary') else ''),
                ("IBAN", employee.get('iban', '')),
                ("Banque", employee.get('bank_name', ''))
            ]),
            
            ("Contacts d'Urgence", [
                ("Nom", employee.get('emergency_name', '')),
                ("Téléphone", employee.get('emergency_phone', '')),
                ("Relation", employee.get('emergency_relation', ''))
            ]),
            
            ("Informations Système", [
                ("Rôle", employee.get('role', 'employe')),
                ("Statut", "🟢 Actif" if employee.get('is_active', False) else "🔴 Inactif"),
                ("Dernière Connexion", employee.get('last_login', 'Jamais')),
                ("Date Création", employee.get('created_at', '')),
                ("Date Modification", employee.get('updated_at', ''))
            ])
        ]
        
        for section_title, fields in sections:
            section_frame = ctk.CTkFrame(parent)
            section_frame.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                section_frame,
                text=section_title,
                font=("Segoe UI", 14, "bold"),
                text_color=Config.PRIMARY_COLOR
            ).pack(anchor="w", padx=20, pady=(15, 10))
            
            # Grille pour les champs
            grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            for i, (label, value) in enumerate(fields):
                row = i // 2
                col = (i % 2) * 2
                
                # Label
                ctk.CTkLabel(
                    grid_frame,
                    text=label + ":",
                    font=("Segoe UI", 11, "bold"),
                    anchor="w"
                ).grid(row=row, column=col, padx=(0, 10), pady=5, sticky="w")
                
                # Valeur
                ctk.CTkLabel(
                    grid_frame,
                    text=str(value) if value not in [None, ''] else "Non renseigné",
                    font=("Segoe UI", 11),
                    anchor="w"
                ).grid(row=row, column=col + 1, padx=(0, 20), pady=5, sticky="w")
            
            # Configurer les colonnes
            grid_frame.grid_columnconfigure(1, weight=1)
            grid_frame.grid_columnconfigure(3, weight=1)
    
    def show_create_form(self):
        """Afficher le formulaire de création d'employé"""
        self.create_form_window = ctk.CTkToplevel(self.master)
        self.create_form_window.title("Nouvel Employé")
        self.create_form_window.geometry("900x700")
        self.create_form_window.transient(self.master)
        
        # Frame principal avec scroll
        main_frame = ctk.CTkScrollableFrame(self.create_form_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        ctk.CTkLabel(
            main_frame,
            text="📝 Nouvel Employé",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(0, 20))
        
        # Formulaire
        self.create_employee_form(main_frame)
        
        # Boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(
            button_frame,
            text="Enregistrer",
            command=self.save_employee,
            width=120,
            height=45,
            fg_color=Config.SUCCESS_COLOR,
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Annuler",
            command=self.create_form_window.destroy,
            width=120,
            height=45,
            fg_color=Config.DANGER_COLOR
        ).pack(side="left", padx=10)
    
    def create_employee_form(self, parent):
        """Créer le formulaire d'employé"""
        # Dictionnaire pour stocker les champs
        self.form_fields = {}
        
        # Section 1: Informations personnelles
        self.create_form_section(
            parent,
            "Informations Personnelles",
            [
                ("Matricule*", "employee_id", True),
                ("CIN", "cin", False),
                ("Nom*", "last_name", True),
                ("Prénom*", "first_name", True),
                ("Genre", "gender", False, "select", ["", "Homme", "Femme"]),
                ("Date Naissance", "birth_date", False, "date")
            ]
        )
        
        # Section 2: Coordonnées
        self.create_form_section(
            parent,
            "Coordonnées",
            [
                ("Adresse", "address", False),
                ("Ville", "city", False),
                ("Code Postal", "postal_code", False),
                ("Téléphone Personnel", "personal_phone", False),
                ("Email Personnel", "personal_email", False),
                ("Téléphone Professionnel", "work_phone", False),
                ("Email Professionnel", "work_email", False)
            ]
        )
        
        # Section 3: Informations professionnelles
        self.create_form_section(
            parent,
            "Informations Professionnelles",
            [
                ("Date Embauche*", "hire_date", True, "date"),
                ("Type Contrat", "contract_type", False, "select", 
                 ["", "CDI", "CDD", "Stage", "Contrat Pro"]),
                ("Salaire Base", "salary", False, "number"),
                ("IBAN", "iban", False),
                ("Banque", "bank_name", False)
            ]
        )
        
        # Section 4: Département et poste
        dept_frame = ctk.CTkFrame(parent)
        dept_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            dept_frame,
            text="Département et Poste",
            font=("Segoe UI", 16, "bold"),
            text_color=Config.PRIMARY_COLOR
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Charger départements et postes
        departments = self.get_departments()
        positions = self.get_positions()
        
        grid_frame = ctk.CTkFrame(dept_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Département
        ctk.CTkLabel(grid_frame, text="Département:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        dept_options = [""] + [dept['name'] for dept in departments]
        self.form_fields['department'] = ctk.CTkComboBox(grid_frame, values=dept_options, width=200)
        self.form_fields['department'].grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        
        # Poste
        ctk.CTkLabel(grid_frame, text="Poste:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        position_options = [""] + [pos['title'] for pos in positions]
        self.form_fields['position'] = ctk.CTkComboBox(grid_frame, values=position_options, width=200)
        self.form_fields['position'].grid(row=1, column=1, padx=(0, 20), pady=5, sticky="w")
        
        # Section 5: Contacts d'urgence
        self.create_form_section(
            parent,
            "Contacts d'Urgence",
            [
                ("Nom", "emergency_name", False),
                ("Téléphone", "emergency_phone", False),
                ("Relation", "emergency_relation", False)
            ]
        )
        
        # Section 6: Compte système
        self.create_form_section(
            parent,
            "Compte Système",
            [
                ("Mot de passe*", "password", True, "password"),
                ("Confirmer Mot de passe*", "password_confirm", True, "password"),
                ("Rôle", "role", False, "select", ["employee", "hr", "manager", "admin"])
            ]
        )
    
    def create_form_section(self, parent, title, fields):
        """Créer une section du formulaire"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=Config.PRIMARY_COLOR
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Grille pour les champs
        grid_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        for i, (label, field_name, required, *field_type) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label_text = label
            if required:
                label_text = label.replace("*", "") + "*"
            
            ctk.CTkLabel(
                grid_frame,
                text=label_text + ":",
                font=("Segoe UI", 11, "bold"),
                anchor="w"
            ).grid(row=row, column=col, padx=(0, 10), pady=5, sticky="w")
            
            # Champ
            if field_type and field_type[0] == "select":
                options = field_type[1] if len(field_type) > 1 else []
                widget = ctk.CTkComboBox(grid_frame, values=options, width=200)
            elif field_type and field_type[0] == "date":
                widget = DatePicker(grid_frame)
            elif field_type and field_type[0] == "password":
                widget = ctk.CTkEntry(grid_frame, show="•", width=200)
            elif field_type and field_type[0] == "number":
                widget = ctk.CTkEntry(grid_frame, width=200)
            else:
                widget = ctk.CTkEntry(grid_frame, width=200)
            
            widget.grid(row=row, column=col + 1, padx=(0, 20), pady=5, sticky="w")
            self.form_fields[field_name] = widget
        
        # Configurer les colonnes
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(3, weight=1)
    
    def get_positions(self) -> List[Dict]:
        """Récupérer la liste des postes"""
        try:
            db_instance.cursor.execute("SELECT id, title FROM positions ORDER BY title")
            return [dict(row) for row in db_instance.cursor.fetchall()]
        except Exception as e:
            print(f"Erreur récupération postes: {e}")
            return []
    
    def save_employee(self):
        """Sauvegarder un nouvel employé"""
        try:
            # Récupérer les données du formulaire
            employee_data = {}
            
            for field_name, widget in self.form_fields.items():
                if isinstance(widget, DatePicker):
                    value = widget.get_date()
                elif isinstance(widget, ctk.CTkComboBox):
                    value = widget.get()
                else:
                    value = widget.get()
                
                if value:
                    employee_data[field_name] = value
            
            # Validation des mots de passe
            if 'password' in employee_data and 'password_confirm' in employee_data:
                if employee_data['password'] != employee_data['password_confirm']:
                    messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
                    return
                
                # Ne pas envoyer la confirmation
                del employee_data['password_confirm']
            
            # Validation des champs obligatoires
            required_fields = ['employee_id', 'last_name', 'first_name', 'hire_date', 'password']
            missing_fields = [field for field in required_fields if field not in employee_data or not employee_data[field]]
            
            if missing_fields:
                messagebox.showwarning("Champs manquants", 
                    f"Veuillez remplir les champs obligatoires:\n{', '.join(missing_fields)}")
                return
            
            # Validation email
            if 'personal_email' in employee_data:
                if not ValidationUtils.validate_email(employee_data['personal_email']):
                    messagebox.showerror("Erreur", "Email personnel invalide")
                    return
            
            if 'work_email' in employee_data:
                if not ValidationUtils.validate_email(employee_data['work_email']):
                    messagebox.showerror("Erreur", "Email professionnel invalide")
                    return
            
            # Validation téléphone
            if 'personal_phone' in employee_data:
                if not ValidationUtils.validate_phone(employee_data['personal_phone']):
                    messagebox.showerror("Erreur", "Téléphone personnel invalide")
                    return
            
            # Convertir les noms de département et poste en IDs
            if 'department' in employee_data and employee_data['department']:
                dept_name = employee_data.pop('department')
                departments = self.get_departments()
                for dept in departments:
                    if dept['name'] == dept_name:
                        employee_data['department_id'] = dept['id']
                        break
            
            if 'position' in employee_data and employee_data['position']:
                pos_title = employee_data.pop('position')
                positions = self.get_positions()
                for pos in positions:
                    if pos['title'] == pos_title:
                        employee_data['position_id'] = pos['id']
                        break
            
            # Créer l'employé
            success, message = db_instance.create_employee(employee_data)
            
            if success:
                messagebox.showinfo("Succès", message)
                self.create_form_window.destroy()
                self.load_employees()  # Rafraîchir la liste
            else:
                messagebox.showerror("Erreur", message)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création: {e}")
    
    def edit_employee(self, employee_id: str):
        """Modifier un employé"""
        try:
            # Récupérer les données actuelles
            employee = db_instance.get_employee(employee_id)
            if not employee:
                messagebox.showerror("Erreur", "Employé non trouvé")
                return
            
            # Créer une fenêtre de modification
            edit_window = ctk.CTkToplevel(self.master)
            edit_window.title(f"Modifier Employé - {employee_id}")
            edit_window.geometry("800x600")
            edit_window.transient(self.master)
            edit_window.grab_set()
            
            # Frame principal avec scroll
            main_frame = ctk.CTkScrollableFrame(edit_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                main_frame,
                text=f"📝 Modifier {employee['first_name']} {employee['last_name']}",
                font=("Segoe UI", 20, "bold")
            ).pack(pady=(0, 20))
            
            # Formulaire de modification simplifié
            edit_fields = {}
            
            # Informations de base
            base_frame = ctk.CTkFrame(main_frame)
            base_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(
                base_frame,
                text="Informations de base",
                font=("Segoe UI", 16, "bold"),
                text_color=Config.PRIMARY_COLOR
            ).pack(anchor="w", padx=20, pady=(15, 10))
            
            grid_frame = ctk.CTkFrame(base_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            fields = [
                ("Email Professionnel", "work_email", employee.get('work_email', '')),
                ("Téléphone Professionnel", "work_phone", employee.get('work_phone', '')),
                ("Adresse", "address", employee.get('address', '')),
                ("Ville", "city", employee.get('city', '')),
                ("Salaire", "salary", employee.get('salary', ''))
            ]
            
            for i, (label, field_name, current_value) in enumerate(fields):
                row = i // 2
                col = (i % 2) * 2
                
                ctk.CTkLabel(grid_frame, text=label + ":", font=("Segoe UI", 11, "bold")).grid(row=row, column=col, padx=(0, 10), pady=5, sticky="w")
                
                entry = ctk.CTkEntry(grid_frame, width=200)
                entry.insert(0, str(current_value) if current_value is not None else "")
                entry.grid(row=row, column=col + 1, padx=(0, 20), pady=5, sticky="w")
                edit_fields[field_name] = entry
            
            # Boutons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=20)
            
            def save_changes():
                try:
                    updates = {}
                    for field_name, widget in edit_fields.items():
                        value = widget.get()
                        if value and value != str(employee.get(field_name, '')):
                            # Convertir le salaire en float
                            if field_name == 'salary':
                                try:
                                    updates[field_name] = float(value)
                                except ValueError:
                                    messagebox.showerror("Erreur", "Salaire invalide")
                                    return
                            else:
                                updates[field_name] = value
                    
                    if updates:
                        success, message = db_instance.update_employee(employee_id, updates)
                        if success:
                            messagebox.showinfo("Succès", message)
                            edit_window.destroy()
                            self.load_employees()  # Rafraîchir
                        else:
                            messagebox.showerror("Erreur", message)
                    else:
                        messagebox.showinfo("Info", "Aucune modification effectuée")
                        edit_window.destroy()
                        
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")
            
            ctk.CTkButton(
                button_frame,
                text="💾 Enregistrer",
                command=save_changes,
                width=120,
                height=40,
                fg_color=Config.SUCCESS_COLOR
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="❌ Annuler",
                command=edit_window.destroy,
                width=120,
                height=40,
                fg_color=Config.DANGER_COLOR
            ).pack(side="left", padx=10)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'éditer l'employé: {e}")
    
    def show_employee_leaves(self, employee_id: str):
        """Afficher les congés d'un employé"""
        messagebox.showinfo("Info", f"Affichage des congés pour {employee_id} - À implémenter")
    
    def toggle_employee_status(self, employee_id: str, activate: bool):
        """Activer/Désactiver un employé"""
        try:
            action = "activé" if activate else "désactivé"
            
            if messagebox.askyesno("Confirmation", 
                f"Voulez-vous vraiment {action} l'employé {employee_id} ?"):
                
                updates = {'is_active': 1 if activate else 0}
                success, message = db_instance.update_employee(employee_id, updates)
                
                if success:
                    messagebox.showinfo("Succès", f"Employé {action} avec succès")
                    self.load_employees()  # Rafraîchir
                else:
                    messagebox.showerror("Erreur", message)
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de modifier le statut: {e}")