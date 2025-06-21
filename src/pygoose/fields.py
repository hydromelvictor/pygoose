from typing import Any, Type, Union, Callable
from .exceptions import ValidationError

import re

class Field:
    """Classe de base pour tous les champs"""
    
    def __init__(self,
                 field_type: Type = None,
                 required: bool = False,
                 default: Any = None,
                 unique: bool = False,
                 validate: Union[str, Callable] = None,
                 **kwargs):
        self.field_type = field_type
        self.required = required
        self.default = default
        self.unique = unique
        self.validate = validate
        self.options = kwargs
    
    def validate_value(self, value: Any) -> Any:
        """Valide et convertit la valeur"""
        if value is None:
            if self.required:
                raise ValidationError(f"Champ requis")
            return self.default() if callable(self.default) else self.default
        
        # Validation du type
        if self.field_type and not isinstance(value, self.field_type):
            try:
                value = self.field_type(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Type invalide, attendu {self.field_type.__name__}")
        
        # Validation personnalisée
        if self.validate:
            if isinstance(self.validate, str):
                value = self._builtin_validation(value, self.validate)
            elif callable(self.validate):
                value = self.validate(value)
        
        # Validations spécifiques
        self._validate_constraints(value)
        
        return value
    
    def _builtin_validation(self, value: Any, validator: str) -> Any:
        """Validations intégrées"""
        if validator == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                raise ValidationError("Format email invalide")
        
        return value
    
    def _validate_constraints(self, value: Any) -> None:
        """Valide les contraintes spécifiques au type"""
        # Min/Max pour nombres
        if isinstance(value, (int, float)):
            if 'min' in self.options and value < self.options['min']:
                raise ValidationError(f"Valeur trop petite (min: {self.options['min']})")
            if 'max' in self.options and value > self.options['max']:
                raise ValidationError(f"Valeur trop grande (max: {self.options['max']})")
        
        # Min/Max length pour strings
        if isinstance(value, str):
            if 'min_length' in self.options and len(value) < self.options['min_length']:
                raise ValidationError(f"Chaîne trop courte (min: {self.options['min_length']})")
            if 'max_length' in self.options and len(value) > self.options['max_length']:
                raise ValidationError(f"Chaîne trop longue (max: {self.options['max_length']})")
        
        # Enum
        if 'enum' in self.options and value not in self.options['enum']:
            raise ValidationError(f"Valeur non autorisée. Valeurs possibles: {self.options['enum']}")
