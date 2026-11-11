"""
Composants CustomTkinter réutilisables avec style moderne - VERSION CORRIGÉE
"""
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, date
import tkinter as tk
from typing import Optional, Callable

class ModernCard(ctk.CTkFrame):
    """Carte moderne avec icône, titre et valeur"""
    
    def __init__(self, master, title="", value="", icon="📊", 
                 color="#2A8C55", **kwargs):
        # Définir une largeur et hauteur par défaut si non fournies
        kwargs.setdefault('width', 180)
        kwargs.setdefault('height', 140)
        
        super().__init__(master, **kwargs)
        
        self.configure(
            fg_color=("white", "#2B2B2B"),
            corner_radius=15,
            border_width=1,
            border_color=color
        )
        
        # Icône
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI", 28),
            text_color=color
        )
        self.icon_label.pack(pady=(20, 5))
        
        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 12),
            text_color=("gray40", "gray60"),
            wraplength=self.winfo_reqwidth() - 20
        )
        self.title_label.pack(padx=10)
        
        # Valeur
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=("Segoe UI", 32, "bold"),
            text_color=color
        )
        self.value_label.pack(pady=(5, 20))
        
        # Animation au survol
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(fg_color=("#F5F5F5", "#3A3A3A"))
    
    def _on_leave(self, event):
        self.configure(fg_color=("white", "#2B2B2B"))
    
    def update_value(self, new_value):
        """Mettre à jour la valeur affichée"""
        self.value_label.configure(text=str(new_value))

class SidebarButton(ctk.CTkButton):
    """Bouton de sidebar avec icône"""
    
    def __init__(self, master, text="", icon="", command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(
            text=f"  {icon} {text}",
            anchor="w",
            fg_color="transparent",
            hover_color=("#E8F5E9", "#1B5E20"),
            text_color=("gray20", "white"),
            font=("Segoe UI", 14),
            height=45,
            corner_radius=10,
            command=command
        )

class ModernTable:
    """Tableau moderne avec CustomTkinter"""
    
    def __init__(self, master, columns, data=None, height=400):
        self.master = master
        self.columns = columns
        
        # Frame pour la table
        self.frame = ctk.CTkFrame(master, corner_radius=10)
        
        # Treeview avec style moderne
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Modern.Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        
        style.configure("Modern.Treeview.Heading",
            background="#2A8C55",
            foreground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        
        style.map("Modern.Treeview.Heading",
            background=[('active', '#238749')]
        )
        
        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings",
            style="Modern.Treeview",
            height=height
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Configuration des colonnes
        for col in columns:
            display_name = col.replace("_", " ").title()
            self.tree.heading(col, text=display_name)
            self.tree.column(col, width=150, minwidth=100)
        
        # Placement
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        if data:
            self.set_data(data)
    
    def set_data(self, data):
        """Définir les données de la table"""
        # Effacer les données existantes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insérer les nouvelles données
        for row in data:
            if isinstance(row, dict):
                # Si les données sont des dictionnaires
                values = [row.get(col, "") for col in self.columns]
            else:
                # Si les données sont des listes
                values = list(row)
            
            self.tree.insert("", "end", values=values)
    
    def get_selected_item(self):
        """Obtenir l'élément sélectionné"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values']
        return None
    
    def pack(self, **kwargs):
        """Afficher la table"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Afficher la table en grille"""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs):
        """Placer la table"""
        self.frame.place(**kwargs)

class DatePicker(ctk.CTkFrame):
    """Sélecteur de date moderne simplifié"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        # Entry pour la date
        self.date_var = tk.StringVar()
        self.date_entry = ctk.CTkEntry(
            self,
            textvariable=self.date_var,
            placeholder_text="AAAA-MM-JJ",
            width=120
        )
        self.date_entry.pack(side="left", padx=(0, 10))
        
        # Bouton pour sélectionner aujourd'hui
        self.today_btn = ctk.CTkButton(
            self,
            text="Aujourd'hui",
            width=80,
            height=30,
            command=self.set_today
        )
        self.today_btn.pack(side="left")
    
    def get_date(self) -> str:
        """Obtenir la date sélectionnée"""
        return self.date_var.get()
    
    def set_date(self, date_str: str):
        """Définir la date"""
        self.date_var.set(date_str)
    
    def set_today(self):
        """Définir la date d'aujourd'hui"""
        today = date.today().strftime("%Y-%m-%d")
        self.set_date(today)
    
    def clear(self):
        """Effacer la date"""
        self.date_var.set("")

class SearchBar(ctk.CTkFrame):
    """Barre de recherche avec filtre"""
    
    def __init__(self, master, placeholder="Rechercher...", on_search=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        self.on_search = on_search
        
        # Icône de recherche
        ctk.CTkLabel(self, text="🔍", font=("Segoe UI", 16)).pack(side="left", padx=(0, 10))
        
        # Champ de recherche
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text=placeholder,
            width=300
        )
        self.search_entry.pack(side="left")
        
        # Lier l'événement de saisie
        if on_search:
            self.search_entry.bind("<KeyRelease>", lambda e: self._trigger_search())
    
    def _trigger_search(self):
        """Déclencher la recherche"""
        if self.on_search:
            self.on_search(self.search_var.get())
    
    def get_search_text(self) -> str:
        """Obtenir le texte de recherche"""
        return self.search_var.get()
    
    def clear(self):
        """Effacer la recherche"""
        self.search_var.set("")

class FilterCombo(ctk.CTkFrame):
    """Combo box pour les filtres"""
    
    def __init__(self, master, label="Filtrer:", options=None, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        self.on_select = on_select
        
        # Label
        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        
        # Combo box
        self.options = options or []
        self.combo_var = tk.StringVar()
        self.combo = ctk.CTkComboBox(
            self,
            values=self.options,
            variable=self.combo_var,
            width=150,
            command=self._on_selection if on_select else None
        )
        self.combo.pack(side="left")
    
    def _on_selection(self, choice):
        """Gérer la sélection"""
        if self.on_select:
            self.on_select(choice)
    
    def get_selected(self) -> str:
        """Obtenir la valeur sélectionnée"""
        return self.combo_var.get()
    
    def set_options(self, options):
        """Définir les options"""
        self.options = options
        self.combo.configure(values=options)
    
    def clear(self):
        """Effacer la sélection"""
        self.combo_var.set("")

class StatusBadge(ctk.CTkLabel):
    """Badge pour afficher un statut"""
    
    STATUS_COLORS = {
        'active': '#27AE60',
        'inactive': '#E74C3C',
        'pending': '#F39C12',
        'approved': '#2A8C55',
        'rejected': '#C0392B',
        'success': '#27AE60',
        'warning': '#F39C12',
        'error': '#E74C3C',
        'info': '#3498DB'
    }
    
    def __init__(self, master, text="", status="active", **kwargs):
        super().__init__(master, **kwargs)
        
        color = self.STATUS_COLORS.get(status.lower(), '#3498DB')
        
        self.configure(
            text=text,
            font=("Segoe UI", 10, "bold"),
            text_color="white",
            fg_color=color,
            corner_radius=10,
            padx=10,
            pady=2
        )

class LoadingOverlay(ctk.CTkFrame):
    """Overlay de chargement - VERSION CORRIGÉE"""
    
    def __init__(self, master, text="Chargement...", **kwargs):
        super().__init__(master, **kwargs)
        
        # Utiliser une couleur semi-transparente (noir à 70%)
        self.configure(fg_color="#333333")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Indicateur de chargement
        ctk.CTkLabel(
            content_frame,
            text="⏳",
            font=("Segoe UI", 40),
            text_color="white"
        ).pack(pady=(0, 10))
        
        # Texte
        ctk.CTkLabel(
            content_frame,
            text=text,
            font=("Segoe UI", 14),
            text_color="white"
        ).pack()
        
        # Masquer par défaut
        self.place_forget()
    
    def show(self):
        """Afficher l'overlay"""
        self.place(relwidth=1, relheight=1)
        self.lift()
    
    def hide(self):
        """Masquer l'overlay"""
        self.place_forget()

class ConfirmationDialog:
    """Boîte de dialogue de confirmation"""
    
    def __init__(self, parent, title="Confirmation", message="Êtes-vous sûr ?"):
        self.parent = parent
        self.title = title
        self.message = message
        self.result = False
        
    def show(self) -> bool:
        """Afficher la boîte de dialogue et retourner le résultat"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(self.title)
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Centrer la boîte de dialogue
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (400 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Message
        ctk.CTkLabel(
            dialog,
            text=self.message,
            font=("Segoe UI", 14),
            wraplength=350
        ).pack(pady=30, padx=20)
        
        # Boutons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def confirm():
            self.result = True
            dialog.destroy()
        
        def cancel():
            self.result = False
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="Oui",
            command=confirm,
            width=100,
            fg_color="#27AE60"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Non",
            command=cancel,
            width=100,
            fg_color="#E74C3C"
        ).pack(side="left", padx=10)
        
        # Attendre la fermeture de la boîte de dialogue
        self.parent.wait_window(dialog)
        
        return self.result

class Notification:
    """Notification toast"""
    
    def __init__(self, parent, message="", type="info", duration=3000):
        self.parent = parent
        self.message = message
        self.type = type
        self.duration = duration
        
        self.colors = {
            'success': '#27AE60',
            'error': '#E74C3C',
            'warning': '#F39C12',
            'info': '#3498DB'
        }
        
        self.icon = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
    
    def show(self):
        """Afficher la notification"""
        # Créer le toast
        toast = ctk.CTkFrame(self.parent)
        toast.configure(
            fg_color=self.colors.get(self.type, '#3498DB'),
            corner_radius=10,
            border_width=1,
            border_color="white"
        )
        
        # Positionner en haut à droite
        toast.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Contenu
        content_frame = ctk.CTkFrame(toast, fg_color="transparent")
        content_frame.pack(padx=15, pady=10)
        
        ctk.CTkLabel(
            content_frame,
            text=f"{self.icon.get(self.type, 'ℹ️')} {self.message}",
            font=("Segoe UI", 12, "bold"),
            text_color="white"
        ).pack()
        
        # Animation d'apparition
        toast.place(relx=1.5, rely=0.02, anchor="ne")
        toast.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Supprimer après la durée
        def destroy_toast():
            toast.place_forget()
            toast.destroy()
        
        self.parent.after(self.duration, destroy_toast)
