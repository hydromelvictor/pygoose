from typing import Dict, Any, List, Callable, Union
from datetime import datetime
from bson import ObjectId
from .fields import Field
from .exceptions import ValidationError

class Schema:
    """Définit la structure et les règles de validation des documents"""
    
    def __init__(self, definition: Dict[str, Any], options: Dict[str, Any] = None):
        self.definition = definition
        self.options = options or {}
        self.fields = {}
        self.indexes = []
        self.pre_hooks = {}
        self.post_hooks = {}
        self.methods = {}
        self.statics = {}
        self.plugins = {}
        
        # Parser la définition du schéma
        self._parse_definition()
        
        # Ajouter les timestamps si demandé
        if self.options.get('timestamps', False):
            self.fields['created_at'] = Field(datetime, default=datetime.now)
            self.fields['updated_at'] = Field(datetime, default=datetime.now)
    
    def _parse_definition(self):
        """Parse la définition du schéma en champs"""
        for field_name, field_def in self.definition.items():
            self.fields[field_name] = self._parse_field(field_def)
    
    def _parse_field(self, field_def: Any) -> Field:
        """Parse une définition de champ en objet Field"""
        if isinstance(field_def, type):
            # Type simple: str, int, etc.
            return Field(field_type=field_def)
        
        elif isinstance(field_def, str):
            # Type spécial: 'datetime', 'ObjectId'
            if field_def == 'datetime':
                return Field(field_type=datetime)
            elif field_def == 'ObjectId':
                return Field(field_type=ObjectId)
            else:
                return Field(field_type=str)
        
        elif isinstance(field_def, list) and len(field_def) == 1:
            # Array: [str], [int], etc.
            item_type = field_def[0]
            return Field(field_type=list, array_type=item_type)
        
        elif isinstance(field_def, dict):
            if 'type' in field_def:
                # Définition complète: {'type': str, 'required': True, ...}
                field_type = field_def.pop('type')
                if isinstance(field_type, str):
                    if field_type == 'datetime':
                        field_type = datetime
                    elif field_type == 'ObjectId':
                        field_type = ObjectId
                
                # Gestion du default spécial
                if field_def.get('default') == 'now' and field_type == datetime:
                    field_def['default'] = datetime.now
                
                return Field(field_type=field_type, **field_def)
            else:
                # Objet imbriqué
                return Field(field_type=dict, nested_schema=field_def)
        
        else:
            return Field()
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide un document selon le schéma"""
        validated_data = {}
        
        for field_name, field in self.fields.items():
            value = data.get(field_name)
            try:
                validated_data[field_name] = field.validate_value(value)
            except ValidationError as e:
                raise ValidationError(f"Erreur dans le champ '{field_name}': {str(e)}", field_name)
        
        # Ajouter les champs non définis si mode non strict
        if not self.options.get('strict', True):
            for key, value in data.items():
                if key not in validated_data:
                    validated_data[key] = value
        
        return validated_data
    
    def pre(self, action: str, func: Callable):
        """Ajoute un hook pré-action"""
        if action not in self.pre_hooks:
            self.pre_hooks[action] = []
        self.pre_hooks[action].append(func)
        return func
    
    def post(self, action: str, func: Callable):
        """Ajoute un hook post-action"""
        if action not in self.post_hooks:
            self.post_hooks[action] = []
        self.post_hooks[action].append(func)
        return func
    
    def method(self, name: str, func: Callable):
        """Ajoute une méthode d'instance"""
        self.methods[name] = func
        return func
    
    def static(self, name: str, func: Callable):
        """Ajoute une méthode statique"""
        self.statics[name] = func
        return func
    
    def index(self, fields: Union[str, List, Dict], **options):
        """Ajoute un index"""
        self.indexes.append((fields, options))
    
    def plugin(self, name: str, func: Callable):
        """Ajoute un plugin"""
        self.plugins[name] = func
        return func
