"""
Interface de gestion des congés - VERSION FINALE CORRIGÉE
"""
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from database import db_instance
from models import LeaveRequest
from utils import Config, DateUtils, ExportUtils
from ui.components import ModernTable, DatePicker, ModernCard

class LeavesWindow:
    """Fenêtre de gestion des congés"""
    
    def __init__(self, master, user_role: str, user_id: str):
        self.master = master
        self.user_role = user_role
        self.user_id = user_id
        self.leave_requests = []
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface"""
        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre avec onglets
        self.create_tabs()
    
    def create_tabs(self):
        """Créer les onglets de navigation"""
        self.tabview = ctk.CTkTabview(self.frame)
        self.tabview.pack(fill="both", expand=True)
        
        # Onglets selon le rôle
        if self.user_role in ['admin', 'hr']:
            self.tabview.add("📋 Demandes en Attente")
            self.tabview.add("📅 Tous les Congés")
            self.tabview.add("📊 Statistiques")
            self.tabview.add("➕ Nouvelle Demande")
        else:
            self.tabview.add("📋 Mes Demandes")
            self.tabview.add("📊 Mon Solde")
            self.tabview.add("➕ Nouvelle Demande")
        
        # Configurer chaque onglet
        if self.user_role in ['admin', 'hr']:
            self.setup_pending_tab()
            self.setup_all_leaves_tab()
            self.setup_stats_tab()
        else:
            self.setup_my_requests_tab()
            self.setup_my_balance_tab()
        
        # Toujours configurer l'onglet nouvelle demande
        self.setup_new_request_tab()
        
        # Sélectionner le premier onglet
        default_tab = "📋 Demandes en Attente" if self.user_role in ['admin', 'hr'] else "📋 Mes Demandes"
        self.tabview.set(default_tab)
    
    def setup_pending_tab(self):
        """Configurer l'onglet des demandes en attente"""
        tab = self.tabview.tab("📋 Demandes en Attente")
        
        # Barre d'outils
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            toolbar,
            text="Demandes en attente d'approbation",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")
        
        # Bouton rafraîchir
        ctk.CTkButton(
            toolbar,
            text="↻ Rafraîchir",
            command=self.load_pending_leaves,
            width=100,
            height=30
        ).pack(side="right")
        
        # Tableau des demandes en attente
        columns = ["N°", "Employé", "Type", "Période", "Jours", "Date Demande", "Actions"]
        self.pending_table = ModernTable(tab, columns, height=400)
        self.pending_table.pack(fill="both", expand=True)
        
        # Lier le clic sur les actions
        self.pending_table.tree.bind("<Button-1>", self.on_pending_table_click)
        
        # Charger les données initiales
        self.load_pending_leaves()
    
    def setup_all_leaves_tab(self):
        """Configurer l'onglet tous les congés"""
        tab = self.tabview.tab("📅 Tous les Congés")
        
        # Filtres
        filters_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filters_frame.pack(fill="x", pady=(0, 20))
        
        # Période
        ctk.CTkLabel(filters_frame, text="Période:", font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        
        self.start_date_picker = DatePicker(filters_frame)
        self.start_date_picker.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(filters_frame, text="à", font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        
        self.end_date_picker = DatePicker(filters_frame)
        self.end_date_picker.pack(side="left", padx=(0, 10))
        
        # Définir la période par défaut (mois en cours)
        today = date.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year, 12, 31)
        
        self.start_date_picker.set_date(first_day.strftime("%Y-%m-%d"))
        self.end_date_picker.set_date(last_day.strftime("%Y-%m-%d"))
        
        # Bouton filtrer
        ctk.CTkButton(
            filters_frame,
            text="Filtrer",
            command=self.filter_leaves,
            width=80,
            height=30
        ).pack(side="left", padx=(20, 0))
        
        # Bouton exporter
        ctk.CTkButton(
            filters_frame,
            text="📤 Exporter",
            command=self.export_leaves,
            width=100,
            height=30
        ).pack(side="right")
        
        # Tableau tous les congés
        columns = ["N°", "Employé", "Type", "Période", "Jours", "Statut", "Approuvé par", "Date Approbation"]
        self.all_leaves_table = ModernTable(tab, columns, height=400)
        self.all_leaves_table.pack(fill="both", expand=True)
        
        # Charger les données initiales
        self.filter_leaves()
    
    def setup_stats_tab(self):
        """Configurer l'onglet statistiques"""
        tab = self.tabview.tab("📊 Statistiques")
        
        # Statistiques
        stats_frame = ctk.CTkFrame(tab, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Cartes statistiques
        cards_data = [
            ("📅", "Congés ce Mois", "0", Config.PRIMARY_COLOR),
            ("✅", "Approuvés", "0", Config.SUCCESS_COLOR),
            ("⏳", "En Attente", "0", Config.WARNING_COLOR),
            ("❌", "Refusés", "0", Config.DANGER_COLOR)
        ]
        
        for i, (icon, title, value, color) in enumerate(cards_data):
            card = ModernCard(
                stats_frame,
                title=title,
                value=value,
                icon=icon,
                color=color,
                width=180,
                height=140
            )
            card.grid(row=0, column=i, padx=10, sticky="nsew")
        
        # Graphique
        chart_frame = ctk.CTkFrame(tab)
        chart_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        ctk.CTkLabel(
            chart_frame,
            text="Répartition par Type de Congé",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)
        
        # Placeholder pour graphique
        placeholder = ctk.CTkLabel(
            chart_frame,
            text="📊 Graphique des congés par type\n(À implémenter)",
            font=("Segoe UI", 14),
            text_color="gray"
        )
        placeholder.pack(expand=True)
        
        # Charger les statistiques
        self.load_stats()
    
    def setup_my_requests_tab(self):
        """Configurer l'onglet mes demandes"""
        tab = self.tabview.tab("📋 Mes Demandes")
        
        # Barre d'outils
        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            toolbar,
            text="Mes demandes de congé",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")
        
        # Bouton rafraîchir
        ctk.CTkButton(
            toolbar,
            text="↻ Rafraîchir",
            command=self.load_my_requests,
            width=100,
            height=30
        ).pack(side="right")
        
        # Tableau des demandes
        columns = ["N°", "Type", "Période", "Jours", "Statut", "Date Demande", "Actions"]
        self.my_requests_table = ModernTable(tab, columns, height=400)
        self.my_requests_table.pack(fill="both", expand=True)
        
        # Charger les demandes de l'utilisateur
        self.load_my_requests()
    
    def setup_my_balance_tab(self):
        """Configurer l'onglet mon solde"""
        tab = self.tabview.tab("📊 Mon Solde")
        
        # Frame scrollable
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Solde annuel
        annual_frame = ctk.CTkFrame(scroll_frame)
        annual_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            annual_frame,
            text="📅 Congés Annuels",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(20, 20))
        
        # Récupérer le solde
        balance = db_instance.get_leave_balance(self.user_id)
        
        annual_total = balance.get('annual_total', 30)
        annual_taken = balance.get('annual_taken', 0)
        annual_remaining = balance.get('annual_remaining', 30)
        
        # Barre de progression
        progress_frame = ctk.CTkFrame(annual_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(progress_frame, text="Jours acquis:", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(progress_frame, text=str(annual_total), font=("Segoe UI", 14, "bold")).pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(progress_frame, text="Jours pris:", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(progress_frame, text=str(annual_taken), font=("Segoe UI", 14, "bold")).pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(progress_frame, text="Jours restants:", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(
            progress_frame,
            text=str(annual_remaining),
            font=("Segoe UI", 14, "bold"),
            text_color=Config.SUCCESS_COLOR
        ).pack(side="left", padx=(5, 0))
        
        # Progress bar
        progress = ctk.CTkProgressBar(annual_frame)
        progress.pack(fill="x", padx=20, pady=10)
        progress.set(annual_taken / annual_total if annual_total > 0 else 0)
        
        # Autres soldes
        other_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        other_frame.pack(fill="x", pady=(0, 30))
        
        other_balances = [
            ("🏥", "Congés Maladie", f"{balance.get('sick_remaining', 30)}/{balance.get('sick_total', 30)}", Config.DANGER_COLOR),
            ("🎓", "Congés Formation", f"{balance.get('training_remaining', 10)}/{balance.get('training_total', 10)}", Config.WARNING_COLOR),
            ("⭐", "Congés Exceptionnels", f"{balance.get('exceptional_remaining', 5)}/{balance.get('exceptional_total', 5)}", Config.INFO_COLOR)
        ]
        
        for i, (icon, title, value, color) in enumerate(other_balances):
            card = ModernCard(
                other_frame,
                title=title,
                value=value,
                icon=icon,
                color=color,
                width=200,
                height=120
            )
            card.grid(row=0, column=i, padx=10, sticky="nsew")
        
        # Informations
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#2B2B2B", corner_radius=10)
        info_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Informations importantes:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        info_text = """
        • Les congés annuels sont renouvelés chaque année civile
        • Les congés maladie nécessitent un certificat médical
        • Les congés formation doivent être liés à des formations professionnelles
        • Les congés exceptionnels sont pour événements familiaux importants
        """
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))
    
    def setup_new_request_tab(self):
        """Configurer l'onglet nouvelle demande - VERSION CORRIGÉE"""
        tab = self.tabview.tab("➕ Nouvelle Demande")
        
        # Frame scrollable
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titre
        ctk.CTkLabel(
            scroll_frame,
            text="📝 Nouvelle Demande de Congé",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 30))
        
        # Type de congé
        type_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            type_frame,
            text="Type de congé:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        leave_types = [
            ("annual", "Congé Annuel", "#2A8C55"),
            ("sick", "Congé Maladie", "#E74C3C"),
            ("training", "Congé Formation", "#F39C12"),
            ("exceptional", "Congé Exceptionnel", "#1ABC9C")
        ]
        
        self.leave_type_var = tk.StringVar(value="annual")
        
        for leave_id, leave_name, color in leave_types:
            radio = ctk.CTkRadioButton(
                type_frame,
                text=leave_name,
                variable=self.leave_type_var,
                value=leave_id,
                font=("Segoe UI", 13)
            )
            radio.pack(anchor="w", pady=5)
        
        # Période
        period_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        period_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            period_frame,
            text="Période:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Date de début
        start_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        start_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(start_frame, text="Date de début:", font=("Segoe UI", 12)).pack(side="left", padx=(0, 20))
        self.start_date_field = DatePicker(start_frame)
        self.start_date_field.pack(side="left")
        
        # Date de fin
        end_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        end_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(end_frame, text="Date de fin:", font=("Segoe UI", 12)).pack(side="left", padx=(0, 28))
        self.end_date_field = DatePicker(end_frame)
        self.end_date_field.pack(side="left")
        
        # Calcul automatique des jours
        calc_frame = ctk.CTkFrame(period_frame, fg_color="transparent")
        calc_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            calc_frame,
            text="📅 Calculer les jours",
            command=self.calculate_days,
            width=150,
            height=35
        ).pack(side="left")
        
        self.days_label = ctk.CTkLabel(
            calc_frame,
            text="Jours: 0",
            font=("Segoe UI", 14, "bold"),
            text_color=Config.PRIMARY_COLOR
        )
        self.days_label.pack(side="left", padx=(20, 0))
        
        # Motif
        reason_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        reason_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            reason_frame,
            text="Motif (optionnel):",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))
        
        self.reason_text = ctk.CTkTextbox(reason_frame, height=80)
        self.reason_text.pack(fill="x")
        
        # Informations solde
        balance_frame = ctk.CTkFrame(scroll_frame, fg_color="#2B2B2B", corner_radius=10)
        balance_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            balance_frame,
            text="📊 Votre solde de congés:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Récupérer le solde actuel
        balance = db_instance.get_leave_balance(self.user_id)
        balance_info = f"""
        • Congés annuels: {balance.get('annual_remaining', 30)} jours restants
        • Congés maladie: {balance.get('sick_remaining', 30)} jours restants
        • Congés formation: {balance.get('training_remaining', 10)} jours restants
        • Congés exceptionnels: {balance.get('exceptional_remaining', 5)} jours restants
        """
        
        ctk.CTkLabel(
            balance_frame,
            text=balance_info,
            font=("Segoe UI", 12),
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Bouton soumettre
        submit_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        submit_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            submit_frame,
            text="📤 Soumettre la demande",
            command=self.submit_leave_request,
            width=200,
            height=45,
            fg_color=Config.SUCCESS_COLOR,
            font=("Segoe UI", 14, "bold")
        ).pack()
        
        # Info sur la procédure
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Votre demande sera examinée par le service RH. Vous recevrez une notification par email.",
            font=("Segoe UI", 11),
            text_color="gray70",
            wraplength=600
        ).pack()
    
    def load_pending_leaves(self):
        """Charger les demandes en attente"""
        try:
            leaves = db_instance.get_leave_requests(status='pending')
            data = []
            
            for leave in leaves:
                # Période formatée
                start_date = DateUtils.format_date(leave['start_date'])
                end_date = DateUtils.format_date(leave['end_date'])
                period = f"{start_date} au {end_date}"
                
                # Actions
                actions = "✅ ❌"
                
                data.append([
                    leave['request_number'],
                    f"{leave['first_name']} {leave['last_name']}",
                    Config.LEAVE_TYPES.get(leave['leave_type'], {}).get('name', leave['leave_type']),
                    period,
                    leave['total_days'],
                    DateUtils.format_date(leave['created_at'], "%d/%m/%Y %H:%M"),
                    actions
                ])
            
            self.pending_table.set_data(data)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les demandes: {e}")
    
    def load_my_requests(self):
        """Charger mes demandes de congé"""
        try:
            # Récupérer toutes les demandes de l'utilisateur
            query = '''
                SELECT * FROM leave_requests 
                WHERE employee_id = ? 
                ORDER BY created_at DESC
            '''
            db_instance.cursor.execute(query, (self.user_id,))
            leaves = [dict(row) for row in db_instance.cursor.fetchall()]
            
            data = []
            for leave in leaves:
                start_date = DateUtils.format_date(leave['start_date'])
                end_date = DateUtils.format_date(leave['end_date'])
                period = f"{start_date} au {end_date}"
                
                # Statut avec icône
                status_map = {
                    'pending': ('⏳ En attente', Config.WARNING_COLOR),
                    'approved': ('✅ Approuvé', Config.SUCCESS_COLOR),
                    'rejected': ('❌ Rejeté', Config.DANGER_COLOR),
                    'cancelled': ('🚫 Annulé', 'gray')
                }
                
                status_text, _ = status_map.get(leave['status'], (leave['status'], 'black'))
                
                # Actions disponibles (modifier/supprimer seulement si en attente)
                actions = ""
                if leave['status'] == 'pending':
                    actions = "✏️ 🗑️"
                
                data.append([
                    leave['request_number'],
                    Config.LEAVE_TYPES.get(leave['leave_type'], {}).get('name', leave['leave_type']),
                    period,
                    leave['total_days'],
                    status_text,
                    DateUtils.format_date(leave['created_at'], "%d/%m/%Y %H:%M"),
                    actions
                ])
            
            self.my_requests_table.set_data(data)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger vos demandes: {e}")
    
    def load_stats(self):
        """Charger les statistiques"""
        try:
            # Récupérer les congés du mois en cours
            today = date.today()
            first_day = date(today.year, today.month, 1)
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1) if today.month < 12 else date(today.year, 12, 31)
            
            query = '''
                SELECT status, COUNT(*) as count 
                FROM leave_requests 
                WHERE created_at BETWEEN ? AND ?
                GROUP BY status
            '''
            
            db_instance.cursor.execute(query, (first_day.isoformat(), last_day.isoformat()))
            rows = db_instance.cursor.fetchall()
            stats = {row['status']: row['count'] for row in rows}
            
            # Mettre à jour les cartes
            total = sum(stats.values())
            
            # Chercher les cartes dans l'onglet stats
            tab = self.tabview.tab("📊 Statistiques")
            
            # Parcourir les widgets pour trouver les cartes
            for widget in tab.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ModernCard):
                            # Identifier la carte par son titre
                            title = child.title_label.cget("text")
                            if "Congés ce Mois" in title:
                                child.update_value(total)
                            elif "Approuvés" in title:
                                child.update_value(stats.get('approved', 0))
                            elif "En Attente" in title:
                                child.update_value(stats.get('pending', 0))
                            elif "Refusés" in title:
                                child.update_value(stats.get('rejected', 0))
            
        except Exception as e:
            print(f"Erreur chargement statistiques: {e}")
    
    def filter_leaves(self):
        """Filtrer les congés par période"""
        try:
            start_date = self.start_date_picker.get_date()
            end_date = self.end_date_picker.get_date()
            
            if not start_date or not end_date:
                messagebox.showwarning("Erreur", "Veuillez sélectionner une période valide")
                return
            
            # Récupérer tous les congés dans la période
            query = '''
                SELECT lr.*, e.last_name, e.first_name, e.work_email,
                       a.last_name || ' ' || a.first_name as approver_name
                FROM leave_requests lr
                JOIN employees e ON lr.employee_id = e.employee_id
                LEFT JOIN employees a ON lr.approved_by = a.employee_id
                WHERE lr.start_date BETWEEN ? AND ?
                ORDER BY lr.start_date
            '''
            
            db_instance.cursor.execute(query, (start_date, end_date))
            leaves = [dict(row) for row in db_instance.cursor.fetchall()]
            
            # Afficher dans le tableau
            data = []
            for leave in leaves:
                start = DateUtils.format_date(leave['start_date'])
                end = DateUtils.format_date(leave['end_date'])
                period = f"{start} au {end}"
                
                # Statut avec icône
                status_map = {
                    'pending': '⏳ En attente',
                    'approved': '✅ Approuvé',
                    'rejected': '❌ Rejeté',
                    'cancelled': '🚫 Annulé'
                }
                
                status_text = status_map.get(leave['status'], leave['status'])
                approval_date = DateUtils.format_date(leave['approval_date'], "%d/%m/%Y %H:%M") if leave['approval_date'] else ""
                
                data.append([
                    leave['request_number'],
                    f"{leave['first_name']} {leave['last_name']}",
                    Config.LEAVE_TYPES.get(leave['leave_type'], {}).get('name', leave['leave_type']),
                    period,
                    leave['total_days'],
                    status_text,
                    leave.get('approver_name', ''),
                    approval_date
                ])
            
            self.all_leaves_table.set_data(data)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du filtrage: {e}")
    
    def export_leaves(self):
        """Exporter la liste des congés"""
        try:
            # Récupérer les données du tableau
            items = self.all_leaves_table.tree.get_children()
            if not items:
                messagebox.showinfo("Info", "Aucune donnée à exporter")
                return
            
            data = []
            for item in items:
                values = self.all_leaves_table.tree.item(item)['values']
                data.append({
                    'N°': values[0],
                    'Employé': values[1],
                    'Type': values[2],
                    'Période': values[3],
                    'Jours': values[4],
                    'Statut': values[5],
                    'Approuvé par': values[6],
                    'Date Approbation': values[7]
                })
            
            # Exporter
            filename = f"conges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = ExportUtils.export_to_excel(data, filename, "Congés")
            
            if export_path:
                messagebox.showinfo("Succès", f"Données exportées vers:\n{export_path}")
            else:
                messagebox.showerror("Erreur", "Impossible d'exporter les données")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def on_pending_table_click(self, event):
        """Gérer le clic sur le tableau des demandes en attente"""
        region = self.pending_table.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.pending_table.tree.identify_column(event.x)
            item = self.pending_table.tree.identify_row(event.y)
            
            if item and column == "#7":  # Colonne Actions
                values = self.pending_table.tree.item(item)['values']
                request_number = values[0]
                
                # Déterminer quelle action a été cliquée
                x, y = event.x, event.y
                bbox = self.pending_table.tree.bbox(item, column)
                
                if bbox:
                    # Calculer la position relative dans la cellule
                    rel_x = x - bbox[0]
                    cell_width = bbox[2]
                    
                    # Diviser la cellule en 2 pour les 2 actions
                    action_width = cell_width / 2
                    
                    if rel_x < action_width:
                        # Approuver
                        self.approve_leave_request(request_number)
                    else:
                        # Rejeter
                        self.reject_leave_request(request_number)
    
    def approve_leave_request(self, request_number: str):
        """Approuver une demande de congé"""
        try:
            if messagebox.askyesno("Confirmation", f"Approuver la demande {request_number} ?"):
                # Mettre à jour le statut
                updates = {
                    'status': 'approved',
                    'approved_by': self.user_id,
                    'approval_date': datetime.now().isoformat()
                }
                
                # Récupérer l'ID de la demande
                db_instance.cursor.execute("SELECT id FROM leave_requests WHERE request_number = ?", (request_number,))
                result = db_instance.cursor.fetchone()
                
                if result:
                    query = '''
                        UPDATE leave_requests 
                        SET status = ?, approved_by = ?, approval_date = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    '''
                    db_instance.cursor.execute(query, ('approved', self.user_id, updates['approval_date'], result[0]))
                    db_instance.conn.commit()
                    
                    messagebox.showinfo("Succès", f"Demande {request_number} approuvée")
                    self.load_pending_leaves()  # Rafraîchir
                else:
                    messagebox.showerror("Erreur", "Demande non trouvée")
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'approuver la demande: {e}")
    
    def reject_leave_request(self, request_number: str):
        """Rejeter une demande de congé"""
        try:
            # Demander une raison
            from tkinter import simpledialog
            reason = simpledialog.askstring("Raison du rejet", 
                "Veuillez indiquer la raison du rejet:", 
                parent=self.master)
            
            if reason:
                # Mettre à jour le statut
                updates = {
                    'status': 'rejected',
                    'approved_by': self.user_id,
                    'rejection_reason': reason,
                    'approval_date': datetime.now().isoformat()
                }
                
                # Récupérer l'ID de la demande
                db_instance.cursor.execute("SELECT id FROM leave_requests WHERE request_number = ?", (request_number,))
                result = db_instance.cursor.fetchone()
                
                if result:
                    query = '''
                        UPDATE leave_requests 
                        SET status = ?, approved_by = ?, rejection_reason = ?, approval_date = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    '''
                    db_instance.cursor.execute(query, ('rejected', self.user_id, reason, updates['approval_date'], result[0]))
                    db_instance.conn.commit()
                    
                    messagebox.showinfo("Succès", f"Demande {request_number} rejetée")
                    self.load_pending_leaves()  # Rafraîchir
                else:
                    messagebox.showerror("Erreur", "Demande non trouvée")
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de rejeter la demande: {e}")
    
    def calculate_days(self):
        """Calculer le nombre de jours entre deux dates"""
        try:
            start_date = self.start_date_field.get_date()
            end_date = self.end_date_field.get_date()
            
            if not start_date or not end_date:
                messagebox.showwarning("Erreur", "Veuillez sélectionner les dates")
                return
            
            days = DateUtils.calculate_working_days(start_date, end_date)
            self.days_label.configure(text=f"Jours: {days}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur calcul jours: {e}")
    
    def submit_leave_request(self):
        """Soumettre une demande de congé"""
        try:
            # Récupérer les données
            leave_type = self.leave_type_var.get()
            start_date = self.start_date_field.get_date()
            end_date = self.end_date_field.get_date()
            reason = self.reason_text.get("1.0", "end-1c").strip()
            
            # Validation
            if not start_date or not end_date:
                messagebox.showwarning("Erreur", "Veuillez sélectionner les dates")
                return
            
            # Calculer les jours
            total_days = DateUtils.calculate_working_days(start_date, end_date)
            if total_days <= 0:
                messagebox.showwarning("Erreur", "Période invalide ou jours ouvrables nuls")
                return
            
            # Vérifier le solde
            balance = db_instance.get_leave_balance(self.user_id)
            if not self.check_balance(leave_type, total_days, balance):
                return
            
            # Créer la demande
            request_data = {
                'employee_id': self.user_id,
                'leave_type': leave_type,
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days,
                'reason': reason if reason else None,
                'status': 'pending'
            }
            
            # Sauvegarder
            success, message = db_instance.create_leave_request(request_data)
            
            if success:
                messagebox.showinfo("Succès", 
                    f"✅ Demande soumise avec succès!\n\n"
                    f"📋 Numéro: {message}\n"
                    f"📅 Type: {Config.LEAVE_TYPES.get(leave_type, {}).get('name', leave_type)}\n"
                    f"📆 Période: {DateUtils.format_date(start_date)} au {DateUtils.format_date(end_date)}\n"
                    f"📊 Jours: {total_days}\n\n"
                    f"Elle sera traitée par le service RH.")
                
                # Réinitialiser le formulaire
                self.reset_form()
                
                # Rafraîchir les onglets
                if self.user_role in ['admin', 'hr']:
                    self.load_pending_leaves()
                else:
                    self.load_my_requests()
                    
            else:
                messagebox.showerror("Erreur", f"❌ {message}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur lors de la soumission: {e}")
    
    def check_balance(self, leave_type: str, requested_days: int, balance: Dict) -> bool:
        """Vérifier le solde de congés"""
        if leave_type == 'annual':
            remaining = balance.get('annual_remaining', 0)
            if requested_days > remaining:
                messagebox.showerror(
                    "❌ Solde insuffisant",
                    f"Solde annuel insuffisant!\n\n"
                    f"📊 Demandé: {requested_days} jours\n"
                    f"📈 Disponible: {remaining} jours\n\n"
                    f"Veuillez ajuster vos dates ou choisir un autre type de congé."
                )
                return False
        elif leave_type == 'sick':
            remaining = balance.get('sick_remaining', 0)
            if requested_days > remaining:
                messagebox.showerror(
                    "❌ Solde insuffisant",
                    f"Solde maladie insuffisant!\n\n"
                    f"📊 Demandé: {requested_days} jours\n"
                    f"📈 Disponible: {remaining} jours"
                )
                return False
        elif leave_type == 'training':
            remaining = balance.get('training_remaining', 0)
            if requested_days > remaining:
                messagebox.showerror(
                    "❌ Solde insuffisant",
                    f"Solde formation insuffisant!\n\n"
                    f"📊 Demandé: {requested_days} jours\n"
                    f"📈 Disponible: {remaining} jours"
                )
                return False
        elif leave_type == 'exceptional':
            remaining = balance.get('exceptional_remaining', 0)
            if requested_days > remaining:
                messagebox.showerror(
                    "❌ Solde insuffisant",
                    f"Solde exceptionnel insuffisant!\n\n"
                    f"📊 Demandé: {requested_days} jours\n"
                    f"📈 Disponible: {remaining} jours"
                )
                return False
        
        return True
    
    def reset_form(self):
        """Réinitialiser le formulaire"""
        self.leave_type_var.set("annual")
        self.start_date_field.set_date("")
        self.end_date_field.set_date("")
        self.reason_text.delete("1.0", "end")
        self.days_label.configure(text="Jours: 0")
