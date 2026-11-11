"""Modèles de données avec validation - VERSION FINALE
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import re

@dataclass
class Employee:
    """Modèle Employé avec validation"""
    employee_id: str = ""
    last_name: str = ""
    first_name: str = ""
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    personal_email: Optional[str] = None
    work_email: Optional[str] = None
    personal_phone: Optional[str] = None
    work_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    cin: Optional[str] = None
    nationality: Optional[str] = None
    hire_date: Optional[str] = None
    contract_type: Optional[str] = None
    contract_end: Optional[str] = None
    position_id: Optional[int] = None
    department_id: Optional[int] = None
    salary: Optional[float] = None
    marital_status: Optional[str] = None
    children_count: int = 0
    emergency_name: Optional[str] = None
    emergency_phone: Optional[str] = None
    emergency_relation: Optional[str] = None
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    role: str = "employee"
    is_active: bool = True
    password: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Valider les données de l'employé"""
        errors = []
        
        if not self.employee_id:
            errors.append("L'ID employé est obligatoire")
        
        if not self.last_name or len(self.last_name) < 2:
            errors.append("Le nom est obligatoire (min 2 caractères)")
        
        if not self.first_name or len(self.first_name) < 2:
            errors.append("Le prénom est obligatoire (min 2 caractères)")
        
        if self.personal_email and not self._is_valid_email(self.personal_email):
            errors.append("Email personnel invalide")
        
        if self.work_email and not self._is_valid_email(self.work_email):
            errors.append("Email professionnel invalide")
        
        if self.personal_phone and not self._is_valid_phone(self.personal_phone):
            errors.append("Téléphone personnel invalide")
        
        if self.hire_date:
            try:
                datetime.strptime(self.hire_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Date d'embauche invalide (format: AAAA-MM-JJ)")
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Valider un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Valider un numéro de téléphone"""
        if not phone:
            return True
        # Supprimer les espaces et caractères spéciaux
        cleaned = re.sub(r'[^\d+]', '', phone)
        return len(cleaned) >= 8 and len(cleaned) <= 15
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour affichage"""
        data = self.__dict__.copy()
        # Retirer le mot de passe pour la sécurité
        data.pop('password', None)
        return data
    
    def to_employee_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour insertion DB"""
        data = {
            'employee_id': self.employee_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'personal_email': self.personal_email,
            'work_email': self.work_email,
            'personal_phone': self.personal_phone,
            'work_phone': self.work_phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'cin': self.cin,
            'nationality': self.nationality,
            'hire_date': self.hire_date,
            'contract_type': self.contract_type,
            'contract_end': self.contract_end,
            'position_id': self.position_id,
            'department_id': self.department_id,
            'salary': self.salary,
            'marital_status': self.marital_status,
            'children_count': self.children_count,
            'emergency_name': self.emergency_name,
            'emergency_phone': self.emergency_phone,
            'emergency_relation': self.emergency_relation,
            'bank_name': self.bank_name,
            'iban': self.iban,
            'role': self.role,
            'is_active': 1 if self.is_active else 0,
            'password': self.password
        }
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class LeaveRequest:
    """Modèle Demande de congé"""
    request_number: str = ""
    employee_id: str = ""
    leave_type: str = "annual"
    start_date: str = ""
    end_date: str = ""
    total_days: int = 0
    reason: Optional[str] = None
    status: str = "pending"
    
    def validate(self) -> List[str]:
        """Valider la demande de congé"""
        errors = []
        
        if not self.employee_id:
            errors.append("ID employé obligatoire")
        
        if not self.start_date:
            errors.append("Date de début obligatoire")
        else:
            try:
                start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
                if start < date.today():
                    errors.append("La date de début ne peut pas être dans le passé")
            except ValueError:
                errors.append("Date de début invalide (format: AAAA-MM-JJ)")
        
        if not self.end_date:
            errors.append("Date de fin obligatoire")
        else:
            try:
                end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
                if self.start_date:
                    start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
                    if end < start:
                        errors.append("La date de fin doit être après la date de début")
            except ValueError:
                errors.append("Date de fin invalide (format: AAAA-MM-JJ)")
        
        if self.total_days <= 0:
            errors.append("Nombre de jours doit être positif")
        
        valid_types = ['annual', 'sick', 'maternity', 'paternity', 'training', 'exceptional']
        if self.leave_type not in valid_types:
            errors.append(f"Type de congé invalide. Types valides: {', '.join(valid_types)}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire pour insertion DB"""
        data = {
            'request_number': self.request_number,
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_days': self.total_days,
            'reason': self.reason,
            'status': self.status
        }
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class Department:
    """Modèle Département"""
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    description: Optional[str] = None
    manager_id: Optional[str] = None
    budget: float = 0.0
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'manager_id': self.manager_id,
            'budget': self.budget,
            'is_active': self.is_active
        }

@dataclass
class Position:
    """Modèle Poste"""
    id: Optional[int] = None
    code: str = ""
    title: str = ""
    description: Optional[str] = None
    department_id: Optional[int] = None
    grade: Optional[str] = None
    salary_min: float = 0.0
    salary_max: float = 0.0
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'department_id': self.department_id,
            'grade': self.grade,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'is_active': self.is_active
        }