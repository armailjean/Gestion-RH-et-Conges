"""
Interface de connexion moderne inspirée de la maquette CLINIK - VERSION FINALE
"""
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk

from auth import auth_manager

class LoginWindow:
    """Fenêtre de connexion moderne"""
    
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = None
        self.setup_ui()
    
    def setup_ui(self):
        """Configurer l'interface de connexion"""
        self.window = ctk.CTk()
        self.window.title("CLINIK RH - Connexion")
        self.window.geometry("450x600")
        
        # Empêcher le redimensionnement
        self.window.resizable(False, False)
        
        # Centrer la fenêtre
        self._center_window()
        
        # Appliquer le thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo/En-tête
        self._create_header(main_frame)
        
        # Formulaire de connexion
        self._create_login_form(main_frame)
        
        # Pied de page
        self._create_footer(main_frame)
        
        # Focus sur le premier champ
        self.window.after(100, lambda: self.entry_employee_id.focus())
        
        # Lier la touche Entrée
        self.window.bind('<Return>', lambda e: self.login())
    
    def _center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_header(self, parent):
        """Créer l'en-tête avec logo"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(pady=(0, 40))
        
        # Titre principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="CLINIK",
            font=("Segoe UI", 42, "bold"),
            text_color="#2A8C55"
        )
        title_label.pack()
        
        # Sous-titre
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Gestion des Ressources Humaines",
            font=("Segoe UI", 14),
            text_color="gray70"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Version
        version_label = ctk.CTkLabel(
            header_frame,
            text="Version Enterprise 1.0.0",
            font=("Segoe UI", 10),
            text_color="gray50"
        )
        version_label.pack(pady=(20, 0))
    
    def _create_login_form(self, parent):
        """Créer le formulaire de connexion"""
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 30))
        
        # Champ ID Employé
        ctk.CTkLabel(
            form_frame,
            text="Identifiant Employé",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.entry_employee_id = ctk.CTkEntry(
            form_frame,
            placeholder_text="Votre ID employé (ex: EMP24001)",
            height=45,
            font=("Segoe UI", 13),
            corner_radius=10
        )
        self.entry_employee_id.pack(fill="x", pady=(0, 15))
        
        # Champ Mot de passe
        password_header = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_header.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            password_header,
            text="Mot de passe",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        
        # Lien mot de passe oublié
        forgot_link = ctk.CTkButton(
            password_header,
            text="Mot de passe oublié ?",
            command=self._show_forgot_password,
            fg_color="transparent",
            text_color="#3498DB",
            hover=False,
            font=("Segoe UI", 11)
        )
        forgot_link.pack(side="right")
        
        self.entry_password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Votre mot de passe",
            show="•",
            height=45,
            font=("Segoe UI", 13),
            corner_radius=10
        )
        self.entry_password.pack(fill="x", pady=(0, 25))
        
        # Bouton de connexion
        self.login_button = ctk.CTkButton(
            form_frame,
            text="SE CONNECTER",
            command=self.login,
            height=50,
            font=("Segoe UI", 14, "bold"),
            fg_color="#2A8C55",
            hover_color="#238749",
            corner_radius=10
        )
        self.login_button.pack(fill="x")
        
        # Séparateur
        separator = ctk.CTkFrame(form_frame, height=1, fg_color="gray30")
        separator.pack(fill="x", pady=25)
        
        # Informations système
        info_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        info_frame.pack(fill="x")
        
        # Affichage des comptes de démo
        demo_info = ctk.CTkLabel(
            info_frame,
            text="🔐 Comptes de démo:\n• ADMIN001 / Admin@2024 (Admin)\n• RH001 / Rh@2024 (RH)\n• EMP24001 / Password123 (Employé)",
            font=("Segoe UI", 10),
            text_color="gray60",
            justify="left"
        )
        demo_info.pack(anchor="w")
    
    def _create_footer(self, parent):
        """Créer le pied de page"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=20)
        
        # Sélecteur de thème
        theme_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            theme_frame,
            text="Thème:",
            font=("Segoe UI", 11)
        ).pack(side="left", padx=(0, 10))
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Mode sombre",
            command=self._toggle_theme,
            font=("Segoe UI", 11)
        )
        self.theme_switch.pack(side="left")
        self.theme_switch.select()  # Mode sombre par défaut
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 CLINIK Corporation. Tous droits réservés.",
            font=("Segoe UI", 10),
            text_color="gray50"
        )
        copyright_label.pack()
        
        # Version API
        api_label = ctk.CTkLabel(
            footer_frame,
            text="API v2.1 • Base de données: SQLite Enterprise",
            font=("Segoe UI", 9),
            text_color="gray40"
        )
        api_label.pack(pady=(5, 0))
    
    def login(self):
        """Gérer la tentative de connexion"""
        employee_id = self.entry_employee_id.get().strip()
        password = self.entry_password.get().strip()
        
        # Validation
        if not employee_id:
            messagebox.showwarning("Champ requis", "Veuillez saisir votre ID employé")
            self.entry_employee_id.focus_set()
            return
        
        if not password:
            messagebox.showwarning("Champ requis", "Veuillez saisir votre mot de passe")
            self.entry_password.focus_set()
            return
        
        # Désactiver le bouton pendant la tentative
        original_text = self.login_button.cget("text")
        self.login_button.configure(
            text="Connexion en cours...",
            state="disabled"
        )
        self.window.update()
        
        try:
            # Tentative d'authentification
            user = auth_manager.login(employee_id, password)
            
            if user:
                messagebox.showinfo(
                    "Connexion réussie",
                    f"Bienvenue {user['first_name']} {user['last_name']}!\n"
                    f"Rôle: {user['role'].upper()}\n"
                    f"Dernière connexion: {user.get('last_login', 'Première connexion')}"
                )
                self.window.destroy()
                self.on_login_success(user)
            else:
                messagebox.showerror(
                    "Échec de connexion",
                    "ID employé ou mot de passe incorrect.\n"
                    "Veuillez vérifier vos identifiants."
                )
                self.entry_password.delete(0, tk.END)
                self.entry_password.focus_set()
        
        except Exception as e:
            messagebox.showerror(
                "Erreur système",
                f"Une erreur est survenue lors de la connexion:\n{str(e)}"
            )
        
        finally:
            # Réactiver le bouton
            self.login_button.configure(
                text=original_text,
                state="normal"
            )
    
    def _show_forgot_password(self):
        """Afficher la fenêtre de réinitialisation de mot de passe"""
        from tkinter import simpledialog
        
        employee_id = simpledialog.askstring(
            "Réinitialisation du mot de passe",
            "Entrez votre ID employé:",
            parent=self.window
        )
        
        if employee_id:
            from database import db_instance
            success, result = db_instance.reset_password(employee_id)
            
            if success:
                messagebox.showinfo(
                    "Mot de passe réinitialisé",
                    f"Un nouveau mot de passe a été généré:\n\n"
                    f"{result}\n\n"
                    f"Veuillez le changer après votre prochaine connexion."
                )
            else:
                messagebox.showwarning(
                    "Employé non trouvé",
                    "ID employé introuvable ou non actif."
                )
    
    def _toggle_theme(self):
        """Basculer entre les thèmes sombre/clair"""
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def run(self):
        """Lancer la fenêtre de connexion"""
        self.window.mainloop()
