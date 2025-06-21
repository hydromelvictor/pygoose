from typing import Dict, Any
from datetime import datetime
from .exceptions import ValidationError

class Document:
    """Représente un document MongoDB avec validation et méthodes"""
    
    def __init__(self, model, data: Dict[str, Any] = None, from_db: bool = False):
        self._model = model
        self._schema = model._schema
        self._data = {}
        self._original_data = {}
        self._modified_fields = set()
        self._is_new = not from_db
        
        if data:
            if from_db:
                # Données venant de la DB, pas besoin de validation
                self._data = data.copy()
                self._original_data = data.copy()
            else:
                # Nouvelles données, validation nécessaire
                self._data = self._schema.validate(data)
                if self._is_new:
                    self._modified_fields = set(self._data.keys())
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return super().__getattribute__(name)
        
        # Méthodes du schéma
        if name in self._schema.methods:
            return lambda *args, **kwargs: self._schema.methods[name](self, *args, **kwargs)
        
        # Données du document
        if name in self._data:
            return self._data[name]
        
        # Champ avec valeur par défaut
        if name in self._schema.fields:
            field = self._schema.fields[name]
            if field.default is not None:
                default_value = field.default() if callable(field.default) else field.default
                self._data[name] = default_value
                return default_value
        
        raise AttributeError(f"'{self.__class__.__name__}' n'a pas d'attribut '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Valider la nouvelle valeur
        if name in self._schema.fields:
            try:
                validated_value = self._schema.fields[name].validate_value(value)
                self._data[name] = validated_value
                self._modified_fields.add(name)
                
                # Mettre à jour updated_at si timestamps activés
                if self._schema.options.get('timestamps') and name != 'updated_at':
                    self._data['updated_at'] = datetime.now()
                    self._modified_fields.add('updated_at')
                    
            except ValidationError as e:
                raise ValidationError(f"Erreur dans le champ '{name}': {str(e)}", name)
        else:
            # Mode non strict
            if not self._schema.options.get('strict', True):
                self._data[name] = value
                self._modified_fields.add(name)
            else:
                raise AttributeError(f"Champ '{name}' non défini dans le schéma")
    
    def save(self) -> 'Document':
        """Sauvegarde le document"""
        # Hooks pré-sauvegarde
        self._run_hooks('pre', 'save')
        
        if self._is_new:
            # Insertion
            result = self._model._collection.insert_one(self._data)
            self._data['_id'] = result.inserted_id
            self._is_new = False
        else:
            # Mise à jour
            if self._modified_fields:
                update_data = {k: self._data[k] for k in self._modified_fields}
                self._model._collection.update_one(
                    {'_id': self._data['_id']},
                    {'$set': update_data}
                )
        
        self._modified_fields.clear()
        self._original_data = self._data.copy()
        
        # Hooks post-sauvegarde
        self._run_hooks('post', 'save')
        
        return self
    
    def delete(self) -> None:
        """Supprime le document"""
        if self._is_new:
            raise RuntimeError("Impossible de supprimer un document non sauvegardé")
        
        # Hooks pré-suppression
        self._run_hooks('pre', 'delete')
        
        self._model._collection.delete_one({'_id': self._data['_id']})
        
        # Hooks post-suppression
        self._run_hooks('post', 'delete')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return self._data.copy()
    
    def to_json(self) -> str:
        """Convertit en JSON"""
        import json
        from bson import json_util
        return json.dumps(self._data, default=json_util.default)
    
    def is_modified(self, field: str = None) -> bool:
        """Vérifie si le document ou un champ a été modifié"""
        if field:
            return field in self._modified_fields
        return bool(self._modified_fields)
    
    def _run_hooks(self, when: str, action: str):
        """Exécute les hooks"""
        hooks = getattr(self._schema, f"{when}_hooks", {}).get(action, [])
        for hook in hooks:
            hook(self)
