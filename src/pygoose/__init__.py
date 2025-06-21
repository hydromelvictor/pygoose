"""Pygoose - ODM Python pour MongoDB inspiré de Mongoose"""

from .connection import connect, disconnect
from .schema import Schema
from .model import model
from .fields import *
from .exceptions import *

__version__ = "0.1.0"
__all__ = [
    'connect', 'disconnect', 'Schema', 'model',
    'ValidationError', 'NotFoundError', 'DuplicateKeyError'
]