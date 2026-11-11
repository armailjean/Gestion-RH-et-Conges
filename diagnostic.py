"""
Script de diagnostic complet pour CLINIK RH
"""
import sys
import os
import traceback
from pathlib import Path

print("🔍 DIAGNOSTIC COMPLET CLINIK RH")
print("="*60)

# 1. Vérifier la structure
print("\n📁 STRUCTURE DES DOSSIERS:")
base_dir = Path(".")
required_dirs = [
    "./ui",
    "./data/database",
    "./assets/icons",
    "./assets/images"
]

for dir_path in required_dirs:
    dir_exists = Path(dir_path).exists()
    print(f"  {'✅' if dir_exists else '❌'} {dir_path}")

# 2. Vérifier les fichiers
print("\n📄 FICHIERS REQUIS:")
required_files = [
    "./app.py",
    "./database.py",
    "./auth.py",
    "./models.py",
    "./utils.py",
    "./ui/__init__.py",
    "./ui/login_ui.py",
    "./ui/dashboard_ui.py",
    "./ui/employees_ui.py",
    "./ui/leaves_ui.py",
    "./ui/components.py"
]

for file_path in required_files:
    file_exists = Path(file_path).exists()
    print(f"  {'✅' if file_exists else '❌'} {file_path}")

# 3. Tester les imports
print("\n🧪 TEST DES IMPORTS:")
test_imports = [
    ("customtkinter", "ctk"),
    ("database", "db_instance"),
    ("auth", "auth_manager"),
    ("ui.components", "ModernCard"),
    ("ui.login_ui", "LoginWindow"),
    ("ui.dashboard_ui", "DashboardWindow")
]

for module_name, attr_name in test_imports:
    try:
        if attr_name:
            exec(f"from {module_name} import {attr_name}")
        else:
            exec(f"import {module_name}")
        print(f"  ✅ {module_name}")
    except ImportError as e:
        print(f"  ❌ {module_name}: {e}")
        traceback.print_exc()

# 4. Tester la base de données
print("\n🗄️ TEST BASE DE DONNÉES:")
try:
    from database import db_instance
    if db_instance.db_exists():
        print("  ✅ Base de données existe")
        
        # Tester la connexion
        try:
            db_instance.connect()
            print("  ✅ Connexion DB réussie")
            
            # Tester les tables
            db_instance.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = db_instance.cursor.fetchall()
            print(f"  ✅ Tables trouvées: {len(tables)}")
            for table in tables[:5]:
                print(f"    • {table['name']}")
        except Exception as e:
            print(f"  ❌ Erreur connexion DB: {e}")
    else:
        print("  ❌ Base de données non trouvée")
except Exception as e:
    print(f"  ❌ Erreur import DB: {e}")

# 5. Test d'authentification de base
print("\n🔐 TEST AUTHENTIFICATION BASIQUE:")
try:
    from auth import auth_manager
    from database import db_instance
    
    print("  ✅ Modules auth et database importés")
    
    # Tester les comptes
    test_accounts = [
        ("ADMIN001", "Admin@2024"),
        ("RH001", "Rh@2024"),
        ("EMP24001", "Password123")
    ]
    
    for emp_id, password in test_accounts:
        try:
            user = db_instance.authenticate(emp_id, password)
            if user:
                print(f"  ✅ {emp_id}: Connexion réussie")
                print(f"     • Nom: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"     • Rôle: {user.get('role', 'N/A')}")
            else:
                print(f"  ❌ {emp_id}: Échec d'authentification")
        except Exception as e:
            print(f"  ⚠️ {emp_id}: Erreur: {e}")
            
except Exception as e:
    print(f"  ❌ Erreur test auth: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("💡 CONSEILS DE DÉPANNAGE:")
print("1. Assurez-vous d'être dans le dossier 'clinik_rh_enterprise/'")
print("2. Exécutez: python diagnostic.py")
print("3. Vérifiez que la base de données existe: data/database/clinik_enterprise.db")
print("4. Si problème DB, supprimez le fichier et relancez l'application")
print("="*60)
