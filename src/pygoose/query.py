from typing import Dict, Any, List, Optional, Union
from bson import ObjectId
from pymongo.cursor import Cursor
from .document import Document

class Query:
    """Constructeur de requêtes MongoDB avec API fluide"""
    
    def __init__(self, model, collection):
        self._model = model
        self._collection = collection
        self._filter = {}
        self._projection = None
        self._sort_spec = None
        self._limit_count = None
        self._skip_count = None
        self._populate_fields = []
    
    def find(self, filter_dict: Dict[str, Any] = None) -> 'Query':
        """Ajoute un filtre de recherche"""
        if filter_dict:
            self._filter.update(filter_dict)
        return self
    
    def where(self, field: str, value: Any = None) -> 'Query':
        """Ajoute une condition WHERE"""
        if value is not None:
            self._filter[field] = value
        return self
    
    def select(self, fields: Union[str, List[str], Dict[str, int]]) -> 'Query':
        """Sélectionne les champs à retourner"""
        if isinstance(fields, str):
            self._projection = {fields: 1}
        elif isinstance(fields, list):
            self._projection = {field: 1 for field in fields}
        elif isinstance(fields, dict):
            self._projection = fields
        return self
    
    def sort(self, field: Union[str, Dict[str, int]]) -> 'Query':
        """Trie les résultats"""
        if isinstance(field, str):
            direction = -1 if field.startswith('-') else 1
            field_name = field.lstrip('-')
            self._sort_spec = [(field_name, direction)]
        elif isinstance(field, dict):
            self._sort_spec = list(field.items())
        return self
    
    def limit(self, count: int) -> 'Query':
        """Limite le nombre de résultats"""
        self._limit_count = count
        return self
    
    def skip(self, count: int) -> 'Query':
        """Ignore les premiers résultats"""
        self._skip_count = count
        return self
    
    def populate(self, field: str) -> 'Query':
        """Marque un champ pour population"""
        self._populate_fields.append(field)
        return self
    
    def exec(self) -> List[Document]:
        """Exécute la requête et retourne les documents"""
        cursor = self._collection.find(self._filter, self._projection)
        
        if self._sort_spec:
            cursor = cursor.sort(self._sort_spec)
        if self._skip_count:
            cursor = cursor.skip(self._skip_count)
        if self._limit_count:
            cursor = cursor.limit(self._limit_count)
        
        documents = []
        for doc_data in cursor:
            doc = Document(self._model, doc_data, from_db=True)
            # TODO: Implémenter la population
            documents.append(doc)
        
        return documents
    
    def first(self) -> Optional[Document]:
        """Retourne le premier document ou None"""
        results = self.limit(1).exec()
        return results[0] if results else None
    
    def count(self) -> int:
        """Compte les documents correspondants"""
        return self._collection.count_documents(self._filter)