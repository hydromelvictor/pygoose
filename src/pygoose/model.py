from typing import Dict, Any, List, Optional, Union
from bson import ObjectId
from datetime import datetime
from .connection import get_database
from .document import Document
from .query import Query
from .exceptions import DuplicateKeyError
from pymongo.errors import DuplicateKeyError as PyMongoDuplicateKeyError

class Model:
    """Modèle pour interagir avec une collection MongoDB"""
    
    def __init__(self, name: str, schema, collection_name: str = None):
        self._name = name
        self._schema = schema
        self._collection_name = collection_name or name.lower() + 's'
        self._collection = None
        self._setup_collection()
    
    def _setup_collection(self):
        """Configure la collection MongoDB"""
        db = get_database()
        self._collection = db[self._collection_name]
        
        # Créer les index
        for index_spec, options in self._schema.indexes:
            self._collection.create_index(index_spec, **options)
    
    def create(self, data: Dict[str, Any]) -> Document:
        """Crée et sauvegarde un nouveau document"""
        doc = Document(self, data)
        return doc.save()
    
    def create_many(self, data_list: List[Dict[str, Any]]) -> List[Document]:
        """Crée plusieurs documents"""
        documents = []
        validated_data = []
        
        for data in data_list:
            validated = self._schema.validate(data)
            validated_data.append(validated)
        
        try:
            result = self._collection.insert_many(validated_data)
            for i, inserted_id in enumerate(result.inserted_ids):
                validated_data[i]['_id'] = inserted_id
                doc = Document(self, validated_data[i], from_db=True)
                documents.append(doc)
        except PyMongoDuplicateKeyError:
            raise DuplicateKeyError("Clé dupliquée lors de l'insertion")
        
        return documents
    
    def find(self, filter_dict: Dict[str, Any] = None) -> Query:
        """Retourne un objet Query pour construire la requête"""
        query = Query(self, self._collection)
        if filter_dict:
            query.find(filter_dict)
        return query
    
    def find_one(self, filter_dict: Dict[str, Any] = None) -> Optional[Document]:
        """Trouve un seul document"""
        doc_data = self._collection.find_one(filter_dict or {})
        if doc_data:
            return Document(self, doc_data, from_db=True)
        return None
    
    def find_by_id(self, doc_id: Union[str, ObjectId]) -> Optional[Document]:
        """Trouve un document par son ID"""
        if isinstance(doc_id, str):
            try:
                doc_id = ObjectId(doc_id)
            except:
                return None
        
        return self.find_one({'_id': doc_id})
    
    def update_one(self, filter_dict: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Met à jour un document"""
        # Ajouter updated_at si timestamps activés
        if self._schema.options.get('timestamps'):
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.now()
        
        result = self._collection.update_one(filter_dict, update)
        return result.modified_count
    
    def update_many(self, filter_dict: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Met à jour plusieurs documents"""
        if self._schema.options.get('timestamps'):
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.now()
        
        result = self._collection.update_many(filter_dict, update)
        return result.modified_count
    
    def delete_one(self, filter_dict: Dict[str, Any]) -> int:
        """Supprime un document"""
        result = self._collection.delete_one(filter_dict)
        return result.deleted_count
    
    def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """Supprime plusieurs documents"""
        result = self._collection.delete_many(filter_dict)
        return result.deleted_count
    
    def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Compte les documents"""
        return self._collection.count_documents(filter_dict or {})
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Exécute une pipeline d'agrégation"""
        return list(self._collection.aggregate(pipeline))
    
    def __call__(self, *args, **kwargs) -> Document:
        """Permet d'instancier avec Model()"""
        if args:
            if isinstance(args[0], dict):
                return Document(self, args[0])
        if kwargs:
            return Document(self, kwargs)
        return Document(self)

# Cache des modèles
_models = {}

def model(name: str, schema, collection_name: str = None) -> Model:
    """Crée ou retourne un modèle"""
    if name in _models:
        return _models[name]
    
    model_instance = Model(name, schema, collection_name)
    _models[name] = model_instance
    
    # Ajouter les méthodes statiques du schéma
    for method_name, method_func in schema.statics.items():
        setattr(model_instance, method_name, method_func.__get__(model_instance, Model))
    
    return model_instance
