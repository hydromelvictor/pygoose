class PyMongooseError(Exception):
    """Exception de base pour PyMongoose"""
    pass

class ValidationError(PyMongooseError):
    """Erreur de validation"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)

class NotFoundError(PyMongooseError):
    """Document non trouvé"""
    pass

class DuplicateKeyError(PyMongooseError):
    """Clé dupliquée"""
    pass
