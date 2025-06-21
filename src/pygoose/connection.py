import pymongo
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class Connection:
    _instance: Optional['Connection'] = None
    _client: Optional[pymongo.MongoClient] = None
    _database: Optional[pymongo.database.Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self, uri: str, options: Dict[str, Any] = None) -> None:
        """Établit la connexion à MongoDB"""
        if options is None:
            options = {}
        
        self._client = pymongo.MongoClient(uri, **options)
        
        # Extraire le nom de la base de données de l'URI
        parsed = urlparse(uri)
        db_name = parsed.path.lstrip('/')
        if not db_name:
            raise ValueError("Nom de base de données requis dans l'URI")
        
        self._database = self._client[db_name]
        
        # Tester la connexion
        self._client.admin.command('ping')
        print(f"Connecté à MongoDB: {db_name}")
    
    def disconnect(self) -> None:
        """Ferme la connexion"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("Déconnecté de MongoDB")
    
    @property
    def database(self) -> pymongo.database.Database:
        if self._database is None:
            raise RuntimeError("Pas de connexion à MongoDB")
        return self._database
    
    @property
    def client(self) -> pymongo.MongoClient:
        if self._client is None:
            raise RuntimeError("Pas de connexion à MongoDB")
        return self._client

# Instance globale
_connection = Connection()

def connect(uri: str, options: Dict[str, Any] = None) -> None:
    """Connecte à MongoDB"""
    _connection.connect(uri, options)

def disconnect() -> None:
    """Déconnecte de MongoDB"""
    _connection.disconnect()

def get_database() -> pymongo.database.Database:
    """Retourne la base de données active"""
    return _connection.database
