"""
Tableau de bord principal inspiré de la maquette CLINIK - VERSION AVEC LOGOUT CALLBACK
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
from typing import List, Dict

from database import db_instance
from ui.components import ModernCard, ModernTable, SidebarButton, LoadingOverlay

class DashboardWindow:
    """Fenêtre du tableau de bord principal"""
    
    def __init__(self, user_data, on_logout_callback=None):
        self.user_data = user_data
        self.on_logout_callback = on_logout_callback  # Nouveau: callback pour logout
        self.window = None
        self.sidebar = None
        self.main_content = None
        self.current_content = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface du tableau de bord"""
        self.window = ctk.CTk()
        self.window.title(f"CLINIK RH - Tableau de bord")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)
        
        # Configuration de la grille
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        
        # Créer la sidebar
        self._create_sidebar()
        
        # Créer le contenu principal
        self._create_main_content()
        
        # Afficher le dashboard par défaut
        self.show_dashboard()
        
        # Centrer la fenêtre
        self._center_window()
    
    def _center_window(self):
        """Centrer la fenêtre"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_sidebar(self):
        """Créer la barre latérale"""
        self.sidebar = ctk.CTkFrame(
            self.window,
            width=280,
            corner_radius=0,
            fg_color=("#2B2B2B", "#1A1A1A")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(30, 20), padx=20)
        
        ctk.CTkLabel(
            logo_frame,
            text="CLINIK",
            font=("Segoe UI", 28, "bold"),
            text_color="#2A8C55"
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Enterprise RH",
            font=("Segoe UI", 12),
            text_color="gray70"
        ).pack(pady=(2, 0))
        
        # Navigation
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=10)
        
        # Boutons de navigation selon le rôle
        if self.user_data['role'] in ['admin', 'hr']:
            nav_items = [
                ("📊 Dashboard", self.show_dashboard),
                ("👥 Employés", self.show_employees),
                ("📅 Congés", self.show_leaves),
                ("📈 Statistiques", self.show_statistics),
                ("📋 Rapports", self.show_reports),
                ("⚙️ Paramètres", self.show_settings)
            ]
        else:
            nav_items = [
                ("📊 Tableau de bord", self.show_dashboard),
                ("👤 Mon profil", self.show_profile),
                ("📅 Mes congés", self.show_my_leaves),
                ("📊 Mon solde", self.show_my_balance),
                ("📝 Demander congé", self.request_leave)
            ]
        
        for text, command in nav_items:
            btn = SidebarButton(
                nav_frame,
                text=text,
                icon=text.split()[0],
                command=command
            )
            btn.pack(fill="x", pady=3)
        
        # Espacement
        ctk.CTkFrame(self.sidebar, height=20, fg_color="transparent").pack()
        
        # Section utilisateur
        self._create_user_section()
    
    def _create_user_section(self):
        """Créer la section utilisateur dans la sidebar"""
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Avatar et info
        avatar_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        avatar_frame.pack(fill="x", pady=(0, 15))
        
        # Avatar circulaire
        avatar = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=("Segoe UI", 24),
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#2A8C55"
        )
        avatar.pack(side="left", padx=(0, 15))
        
        # Info utilisateur
        info_frame = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text=f"{self.user_data['first_name']} {self.user_data['last_name']}",
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"ID: {self.user_data['employee_id']}",
            font=("Segoe UI", 11),
            text_color="gray70",
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Rôle: {self.user_data['role'].upper()}",
            font=("Segoe UI", 11),
            text_color="#2A8C55",
            anchor="w"
        ).pack(anchor="w")
        
        # Bouton déconnexion
        logout_btn = ctk.CTkButton(
            user_frame,
            text="Déconnexion",
            command=self.logout,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            height=40,
            corner_radius=10
        )
        logout_btn.pack(fill="x")
    
    def _create_main_content(self):
        """Créer la zone de contenu principal"""
        self.main_content = ctk.CTkFrame(self.window, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        
        # Configuration de la grille
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(
            self.main_content,
            height=80,
            corner_radius=0,
            fg_color=("white", "#2B2B2B")
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(1, weight=1)
        
        # Titre dynamique
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Tableau de bord",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=40, pady=25, sticky="w")
        
        # Date et heure
        self.datetime_label = ctk.CTkLabel(
            self.header,
            text=self._get_current_datetime(),
            font=("Segoe UI", 12),
            text_color="gray70",
            anchor="e"
        )
        self.datetime_label.grid(row=0, column=1, padx=40, pady=25, sticky="e")
        
        # Mettre à jour l'heure toutes les secondes
        self._update_datetime()
        
        # Zone de contenu déroulante
        self.content_area = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
    
    def _get_current_datetime(self):
        """Obtenir la date et l'heure actuelles formatées"""
        now = datetime.now()
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        months_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        
        day_name = days_fr[now.weekday()]
        month_name = months_fr[now.month - 1]
        
        return f"{day_name} {now.day} {month_name} {now.year} • {now.strftime('%H:%M')}"
    
    def _update_datetime(self):
        """Mettre à jour l'affichage de la date et de l'heure"""
        self.datetime_label.configure(text=self._get_current_datetime())
        self.window.after(1000, self._update_datetime)
    
    def show_dashboard(self):
        """Afficher le tableau de bord"""
        self._clear_content()
        self.title_label.configure(text="Tableau de bord")
        
        # Créer un overlay de chargement
        loading = LoadingOverlay(self.content_area, text="Chargement des données...")
        loading.show()
        self.window.update()
        
        try:
            # Récupérer les statistiques
            stats = db_instance.get_dashboard_stats()
            
            # Cartes statistiques
            stats_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
            stats_frame.pack(fill="x", pady=(0, 30))
            
            cards_data = [
                ("👥", "Employés Actifs", stats.get('total_employees', 0), "#2A8C55"),
                ("📅", "Congés en Attente", stats.get('pending_leaves', 0), "#F39C12"),
                ("🏥", "Absents Aujourd'hui", stats.get('absent_today', 0), "#E74C3C"),
                ("🎉", "Nouveaux ce Mois", stats.get('new_this_month', 0), "#3498DB")
            ]
            
            for i, (icon, title, value, color) in enumerate(cards_data):
                card = ModernCard(
                    stats_frame,
                    title=title,
                    value=value,
                    icon=icon,
                    color=color,
                    width=200,
                    height=150
                )
                card.grid(row=0, column=i, padx=10, sticky="nsew")
            
            # Graphique des départements (placeholder)
            chart_frame = ctk.CTkFrame(self.content_area, height=300)
            chart_frame.pack(fill="x", pady=(0, 30))
            chart_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                chart_frame,
                text="Répartition par Département",
                font=("Segoe UI", 18, "bold")
            ).pack(pady=(20, 15))
            
            # Créer un graphique simple avec des barres colorées
            dept_data = stats.get('by_department', [])
            if dept_data:
                graph_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
                graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                max_count = max((dept['count'] for dept in dept_data), default=1)
                colors = ['#2A8C55', '#3498DB', '#9B59B6', '#E74C3C', '#F39C12']
                
                for i, dept in enumerate(dept_data[:5]):  # Limiter à 5 départements
                    dept_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
                    dept_frame.pack(fill="x", pady=5)
                    
                    # Nom du département
                    ctk.CTkLabel(
                        dept_frame,
                        text=dept['name'],
                        font=("Segoe UI", 12),
                        width=150
                    ).pack(side="left")
                    
                    # Barre de progression
                    progress = min(dept['count'] / max_count, 1.0)
                    progress_bar = ctk.CTkProgressBar(dept_frame)
                    progress_bar.pack(side="left", fill="x", expand=True, padx=10)
                    progress_bar.set(progress)
                    progress_bar.configure(progress_color=colors[i % len(colors)])
                    
                    # Valeur
                    ctk.CTkLabel(
                        dept_frame,
                        text=str(dept['count']),
                        font=("Segoe UI", 12, "bold"),
                        width=50
                    ).pack(side="right")
            else:
                ctk.CTkLabel(
                    chart_frame,
                    text="Aucune donnée disponible",
                    font=("Segoe UI", 14),
                    text_color="gray"
                ).pack(pady=50)
            
            # Dernières activités
            self._create_recent_activity()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le tableau de bord: {e}")
        finally:
            loading.hide()
    
    def _create_recent_activity(self):
        """Afficher les activités récentes"""
        activity_frame = ctk.CTkFrame(self.content_area)
        activity_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        ctk.CTkLabel(
            activity_frame,
            text="Activités Récentes",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(20, 15))
        
        # Tableau des activités
        columns = ["Date", "Action", "Utilisateur", "Détails"]
        
        # Récupérer les dernières demandes de congé comme activités
        try:
            leaves = db_instance.get_leave_requests()[:10]  # 10 dernières
            activities = []
            
            for leave in leaves:
                status_icon = "⏳" if leave['status'] == 'pending' else "✅" if leave['status'] == 'approved' else "❌"
                activities.append([
                    leave['created_at'][:16],
                    f"{status_icon} Demande de congé",
                    leave['employee_id'],
                    f"{leave['leave_type']} - {leave['total_days']} jours"
                ])
            
            if not activities:
                activities = [
                    ["Aucune activité récente", "", "", ""]
                ]
            
        except Exception:
            activities = [
                ["2024-01-15 10:30", "Nouvel employé", "RH001", "Création de EMP24010"],
                ["2024-01-15 09:15", "Congé approuvé", "ADMIN001", "Demande LV2401150001"],
                ["2024-01-14 16:45", "Mise à jour profil", "EMP24005", "Changement d'adresse"],
                ["2024-01-14 14:20", "Nouvelle demande", "EMP24008", "Congé annuel - 5 jours"]
            ]
        
        table = ModernTable(activity_frame, columns, activities, height=200)
        table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def show_employees(self):
        """Afficher la gestion des employés"""
        self._clear_content()
        self.title_label.configure(text="Gestion des Employés")
        
        try:
            from ui.employees_ui import EmployeesWindow
            employees_window = EmployeesWindow(self.content_area, self.user_data['role'])
            
        except ImportError:
            ctk.CTkLabel(
                self.content_area,
                text="Module employés non disponible",
                font=("Segoe UI", 16)
            ).pack(pady=100)
    
    def show_leaves(self):
        """Afficher la gestion des congés"""
        self._clear_content()
        self.title_label.configure(text="Gestion des Congés")
        
        try:
            from ui.leaves_ui import LeavesWindow
            leaves_window = LeavesWindow(self.content_area, self.user_data['role'], self.user_data['employee_id'])
            
        except ImportError:
            ctk.CTkLabel(
                self.content_area,
                text="Module congés non disponible",
                font=("Segoe UI", 16)
            ).pack(pady=100)
    
    def show_statistics(self):
        """Afficher les statistiques"""
        self._clear_content()
        self.title_label.configure(text="📈 Statistiques")
        
        # Frame principal avec onglets
        tabview = ctk.CTkTabview(self.content_area)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Onglet 1: Statistiques générales
        tabview.add("📊 Général")
        self._create_general_stats_tab(tabview.tab("📊 Général"))
        
        # Onglet 2: Statistiques par département
        tabview.add("🏢 Par Département")
        self._create_department_stats_tab(tabview.tab("🏢 Par Département"))
        
        # Onglet 3: Évolution temporelle
        tabview.add("📅 Évolution")
        self._create_trend_stats_tab(tabview.tab("📅 Évolution"))
    
    def _create_general_stats_tab(self, tab):
        """Créer l'onglet de statistiques générales"""
        try:
            # Récupérer les statistiques
            stats = db_instance.get_dashboard_stats()
            employees = db_instance.get_all_employees(active_only=True)
            
            # Frame pour les cartes
            cards_frame = ctk.CTkFrame(tab, fg_color="transparent")
            cards_frame.pack(fill="x", pady=(0, 20))
            
            # Calculer des statistiques supplémentaires
            total_salary = sum(emp.get('salary', 0) for emp in employees if emp.get('salary'))
            avg_salary = total_salary / len(employees) if employees else 0
            
            # Données pour les cartes
            cards_data = [
                ("👥", "Effectif Total", stats.get('total_employees', 0), "#2A8C55"),
                ("💰", "Masse Salariale", f"{total_salary:,.0f} MAD", "#3498DB"),
                ("📊", "Salaire Moyen", f"{avg_salary:,.0f} MAD", "#9B59B6"),
                ("📅", "Congés en Attente", stats.get('pending_leaves', 0), "#F39C12"),
                ("🏥", "Absents Aujourd'hui", stats.get('absent_today', 0), "#E74C3C"),
                ("🎉", "Nouveaux ce Mois", stats.get('new_this_month', 0), "#1ABC9C")
            ]
            
            # Créer les cartes
            for i, (icon, title, value, color) in enumerate(cards_data):
                row = i // 3
                col = i % 3
                
                card = ModernCard(
                    cards_frame,
                    title=title,
                    value=value,
                    icon=icon,
                    color=color,
                    width=180,
                    height=140
                )
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Configurer la grille
            for i in range(3):
                cards_frame.grid_columnconfigure(i, weight=1)
            
            # Distribution par genre
            gender_frame = ctk.CTkFrame(tab)
            gender_frame.pack(fill="both", expand=True, pady=(20, 0))
            
            ctk.CTkLabel(
                gender_frame,
                text="Répartition par Genre",
                font=("Segoe UI", 16, "bold")
            ).pack(pady=(20, 10))
            
            # Calculer la distribution
            gender_counts = {'Homme': 0, 'Femme': 0, 'Autre': 0}
            for emp in employees:
                gender = emp.get('gender', '')
                if gender == 'Homme':
                    gender_counts['Homme'] += 1
                elif gender == 'Femme':
                    gender_counts['Femme'] += 1
                elif gender:
                    gender_counts['Autre'] += 1
            
            # Afficher les résultats
            info_frame = ctk.CTkFrame(gender_frame, fg_color="transparent")
            info_frame.pack(pady=20)
            
            total = sum(gender_counts.values())
            for gender, count in gender_counts.items():
                if count > 0:
                    percentage = (count / total * 100) if total > 0 else 0
                    ctk.CTkLabel(
                        info_frame,
                        text=f"{gender}: {count} ({percentage:.1f}%)",
                        font=("Segoe UI", 14)
                    ).pack(pady=5)
            
        except Exception as e:
            ctk.CTkLabel(
                tab,
                text=f"Erreur chargement statistiques: {str(e)}",
                font=("Segoe UI", 14),
                text_color="red"
            ).pack(pady=100)
    
    def _create_department_stats_tab(self, tab):
        """Créer l'onglet de statistiques par département"""
        try:
            stats = db_instance.get_dashboard_stats()
            dept_data = stats.get('by_department', [])
            
            if not dept_data:
                ctk.CTkLabel(
                    tab,
                    text="Aucune donnée disponible",
                    font=("Segoe UI", 14)
                ).pack(pady=100)
                return
            
            # Tableau des départements
            columns = ["Département", "Effectif", "Pourcentage"]
            
            total_employees = stats.get('total_employees', 1)
            data = []
            
            for dept in dept_data:
                percentage = (dept['count'] / total_employees * 100) if total_employees > 0 else 0
                data.append([
                    dept['name'],
                    dept['count'],
                    f"{percentage:.1f}%"
                ])
            
            table = ModernTable(tab, columns, data, height=300)
            table.pack(fill="both", expand=True, padx=20, pady=20)
            
        except Exception as e:
            ctk.CTkLabel(
                tab,
                text=f"Erreur chargement données: {str(e)}",
                font=("Segoe UI", 14),
                text_color="red"
            ).pack(pady=100)
    
    def _create_trend_stats_tab(self, tab):
        """Créer l'onglet d'évolution temporelle"""
        ctk.CTkLabel(
            tab,
            text="Évolution des effectifs",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)
        
        # Simuler des données historiques
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        employees_count = [45, 47, 50, 52, 55, 58, 60, 62, 65, 68, 70, 72]  # Données simulées
        
        # Créer un graphique simple
        graph_frame = ctk.CTkFrame(tab)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        max_count = max(employees_count) if employees_count else 1
        
        for i, (month, count) in enumerate(zip(months, employees_count)):
            bar_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
            bar_frame.pack(fill="x", pady=2)
            
            # Mois
            ctk.CTkLabel(
                bar_frame,
                text=month,
                font=("Segoe UI", 11),
                width=40
            ).pack(side="left")
            
            # Barre
            bar_height = (count / max_count) * 200
            bar = ctk.CTkFrame(
                bar_frame,
                height=bar_height,
                width=300,
                fg_color="#2A8C55",
                corner_radius=5
            )
            bar.pack(side="left", padx=10)
            
            # Valeur
            ctk.CTkLabel(
                bar_frame,
                text=str(count),
                font=("Segoe UI", 11, "bold"),
                width=40
            ).pack(side="left")
    
    def show_reports(self):
        """Afficher la génération de rapports"""
        self._clear_content()
        self.title_label.configure(text="📋 Rapports")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(
            main_frame,
            text="Génération de Rapports",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=(0, 30))
        
        # Rapports disponibles
        reports = [
            ("📊 Rapport Mensuel", "Synthèse mensuelle des activités RH", self.generate_monthly_report),
            ("👥 Liste des Employés", "Liste complète des employés actifs", self.generate_employee_list),
            ("📅 Congés par Département", "Statistiques des congés par service", self.generate_leave_report),
            ("💰 Analyse Salariale", "Analyse de la masse salariale", self.generate_salary_report)
        ]
        
        for i, (title, description, command) in enumerate(reports):
            report_frame = ctk.CTkFrame(main_frame)
            report_frame.pack(fill="x", pady=10)
            
            # Titre et description
            ctk.CTkLabel(
                report_frame,
                text=title,
                font=("Segoe UI", 16, "bold")
            ).pack(anchor="w", padx=20, pady=(15, 5))
            
            ctk.CTkLabel(
                report_frame,
                text=description,
                font=("Segoe UI", 12),
                text_color="gray70",
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 15))
            
            # Boutons d'export
            btn_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            ctk.CTkButton(
                btn_frame,
                text="📄 Générer",
                command=lambda c=command: c(),
                width=100,
                height=35
            ).pack(side="left", padx=5)
    
    def show_settings(self):
        """Afficher les paramètres"""
        self._clear_content()
        self.title_label.configure(text="⚙️ Paramètres")
        
        ctk.CTkLabel(
            self.content_area,
            text="Paramètres système",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 30))
        
        # Options de paramètres
        settings_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        settings_frame.pack(fill="x", padx=50)
        
        settings_options = [
            ("🔒 Sécurité", "Paramètres de sécurité et mots de passe"),
            ("📊 Interface", "Personnalisation de l'interface"),
            ("🔄 Synchronisation", "Synchronisation des données"),
            ("💾 Sauvegarde", "Configuration des sauvegardes")
        ]
        
        for title, description in settings_options:
            setting_frame = ctk.CTkFrame(settings_frame)
            setting_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                setting_frame,
                text=title,
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", padx=20, pady=(15, 5))
            
            ctk.CTkLabel(
                setting_frame,
                text=description,
                font=("Segoe UI", 12),
                text_color="gray70"
            ).pack(anchor="w", padx=20, pady=(0, 15))
    
    def show_profile(self):
        """Afficher le profil utilisateur"""
        self._clear_content()
        self.title_label.configure(text="👤 Mon Profil")
        
        try:
            # Récupérer les données complètes de l'utilisateur
            from database import db_instance
            employee = db_instance.get_employee(self.user_data['employee_id'])
            
            if not employee:
                ctk.CTkLabel(
                    self.content_area,
                    text="Profil non trouvé",
                    font=("Segoe UI", 16)
                ).pack(pady=100)
                return
            
            # Afficher les informations du profil
            profile_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
            profile_frame.pack(fill="both", expand=True, padx=50, pady=30)
            
            # Photo de profil (placeholder)
            avatar_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
            avatar_frame.pack(pady=(0, 30))
            
            ctk.CTkLabel(
                avatar_frame,
                text="👤",
                font=("Segoe UI", 60),
                width=120,
                height=120,
                corner_radius=60,
                fg_color="#2A8C55"
            ).pack()
            
            # Informations personnelles
            info_frame = ctk.CTkFrame(profile_frame)
            info_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(
                info_frame,
                text="Informations Personnelles",
                font=("Segoe UI", 16, "bold"),
                text_color="#2A8C55"
            ).pack(anchor="w", padx=20, pady=(15, 10))
            
            # Grille d'informations
            grid_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            infos = [
                ("Nom complet:", f"{employee['first_name']} {employee['last_name']}"),
                ("ID Employé:", employee['employee_id']),
                ("Email:", employee.get('work_email', 'Non renseigné')),
                ("Téléphone:", employee.get('work_phone', 'Non renseigné')),
                ("Département:", employee.get('department_name', 'Non renseigné')),
                ("Poste:", employee.get('position_title', 'Non renseigné')),
                ("Date d'embauche:", employee.get('hire_date', 'Non renseigné')),
                ("Rôle:", employee.get('role', 'Non renseigné').upper())
            ]
            
            for i, (label, value) in enumerate(infos):
                row = i // 2
                col = (i % 2) * 2
                
                ctk.CTkLabel(
                    grid_frame,
                    text=label,
                    font=("Segoe UI", 11, "bold"),
                    anchor="w"
                ).grid(row=row, column=col, padx=(0, 10), pady=5, sticky="w")
                
                ctk.CTkLabel(
                    grid_frame,
                    text=value,
                    font=("Segoe UI", 11),
                    anchor="w"
                ).grid(row=row, column=col + 1, padx=(0, 20), pady=5, sticky="w")
            
            # Configurer les colonnes
            grid_frame.grid_columnconfigure(1, weight=1)
            grid_frame.grid_columnconfigure(3, weight=1)
            
            # Bouton modifier le profil
            ctk.CTkButton(
                profile_frame,
                text="📝 Modifier mon profil",
                command=lambda: messagebox.showinfo("Info", "Fonctionnalité à venir"),
                width=200,
                height=40
            ).pack(pady=20)
            
        except Exception as e:
            ctk.CTkLabel(
                self.content_area,
                text=f"Erreur chargement profil: {str(e)}",
                font=("Segoe UI", 14),
                text_color="red"
            ).pack(pady=100)
    
    def show_my_leaves(self):
        """Afficher mes congés"""
        self._clear_content()
        self.title_label.configure(text="📅 Mes Congés")
        
        try:
            from ui.leaves_ui import LeavesWindow
            leaves_window = LeavesWindow(self.content_area, self.user_data['role'], self.user_data['employee_id'])
            
        except ImportError:
            ctk.CTkLabel(
                self.content_area,
                text="Module congés non disponible",
                font=("Segoe UI", 16)
            ).pack(pady=100)
    
    def show_my_balance(self):
        """Afficher mon solde de congés"""
        self._clear_content()
        self.title_label.configure(text="📊 Mon Solde")
        
        try:
            from database import db_instance
            balance = db_instance.get_leave_balance(self.user_data['employee_id'])
            
            balance_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
            balance_frame.pack(fill="both", expand=True, padx=50, pady=30)
            
            ctk.CTkLabel(
                balance_frame,
                text="Solde de vos congés",
                font=("Segoe UI", 20, "bold")
            ).pack(pady=(0, 30))
            
            # Cartes de solde
            cards_data = [
                ("📅", "Congés Annuels", f"{balance.get('annual_remaining', 0)}/{balance.get('annual_total', 30)}", "#2A8C55"),
                ("🏥", "Congés Maladie", f"{balance.get('sick_remaining', 0)}/{balance.get('sick_total', 30)}", "#E74C3C"),
                ("🎓", "Congés Formation", f"{balance.get('training_remaining', 0)}/{balance.get('training_total', 10)}", "#F39C12"),
                ("⭐", "Congés Exceptionnels", f"{balance.get('exceptional_remaining', 0)}/{balance.get('exceptional_total', 5)}", "#1ABC9C")
            ]
            
            for i, (icon, title, value, color) in enumerate(cards_data):
                row = i // 2
                col = i % 2
                
                if 'row_frame' not in locals() or i % 2 == 0:
                    row_frame = ctk.CTkFrame(balance_frame, fg_color="transparent")
                    row_frame.pack(fill="x", pady=10)
                
                card = ModernCard(
                    row_frame,
                    title=title,
                    value=value,
                    icon=icon,
                    color=color,
                    width=250,
                    height=150
                )
                card.grid(row=0, column=col, padx=10, sticky="nsew")
            
        except Exception as e:
            ctk.CTkLabel(
                self.content_area,
                text=f"Erreur chargement solde: {str(e)}",
                font=("Segoe UI", 14),
                text_color="red"
            ).pack(pady=100)
    
    def request_leave(self):
        """Demander un congé"""
        self._clear_content()
        self.title_label.configure(text="📝 Demander un Congé")
        
        try:
            from ui.leaves_ui import LeavesWindow
            leaves_window = LeavesWindow(self.content_area, self.user_data['role'], self.user_data['employee_id'])
            
        except ImportError:
            ctk.CTkLabel(
                self.content_area,
                text="Module congés non disponible",
                font=("Segoe UI", 16)
            ).pack(pady=100)
    
    def generate_monthly_report(self):
        """Générer un rapport mensuel"""
        messagebox.showinfo("Rapport", "Génération du rapport mensuel - À implémenter")
    
    def generate_employee_list(self):
        """Générer la liste des employés"""
        try:
            from utils import ExportUtils
            employees = db_instance.get_all_employees(active_only=True)
            
            if employees:
                filename = f"liste_employes_{date.today().strftime('%Y%m%d')}.xlsx"
                export_path = ExportUtils.export_to_excel(employees, filename, "Employés")
                
                if export_path:
                    messagebox.showinfo("Succès", f"Liste exportée vers:\n{export_path}")
                else:
                    messagebox.showerror("Erreur", "Impossible d'exporter la liste")
            else:
                messagebox.showinfo("Info", "Aucun employé à exporter")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le rapport: {str(e)}")
    
    def generate_leave_report(self):
        """Générer un rapport des congés"""
        messagebox.showinfo("Rapport", "Génération du rapport des congés - À implémenter")
    
    def generate_salary_report(self):
        """Générer un rapport salarial"""
        messagebox.showinfo("Rapport", "Génération du rapport salarial - À implémenter")
    
    def logout(self):
        """Déconnexion avec retour au login - NOUVELLE VERSION"""
        from auth import auth_manager
        
        if messagebox.askyesno("Déconnexion", "Êtes-vous sûr de vouloir vous déconnecter ?"):
            # Utiliser le callback si fourni (retour au login)
            if self.on_logout_callback:
                print("🔒 Déconnexion - Utilisation du callback")
                self.on_logout_callback()
            else:
                # Fallback: Fermer l'application
                auth_manager.logout()
                self.window.destroy()
                print("🔒 Déconnexion - Application fermée")
    
    def _clear_content(self):
        """Effacer le contenu de la zone principale"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def run(self):
        """Lancer la fenêtre"""
        self.window.mainloop()