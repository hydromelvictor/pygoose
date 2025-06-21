"""Exemple d'un système de blog complet"""

from pygoose import connect, Schema, model
from datetime import datetime
from bson import ObjectId

# Connexion
connect('mongodb://localhost:27017/blog_system')

# Schéma Utilisateur
UserSchema = Schema({
    'username': {'type': str, 'required': True, 'unique': True},
    'email': {'type': str, 'required': True, 'unique': True, 'validate': 'email'},
    'password': {'type': str, 'required': True, 'min_length': 6},
    'profile': {
        'display_name': str,
        'bio': str,
        'avatar': str,
        'website': str
    },
    'role': {'type': str, 'enum': ['user', 'admin', 'editor'], 'default': 'user'},
    'is_active': {'type': bool, 'default': True}
}, {'timestamps': True})

# Schéma Catégorie
CategorySchema = Schema({
    'name': {'type': str, 'required': True, 'unique': True},
    'slug': {'type': str, 'required': True, 'unique': True},
    'description': str,
    'color': {'type': str, 'default': '#007bff'}
}, {'timestamps': True})

# Schéma Article
ArticleSchema = Schema({
    'title': {'type': str, 'required': True, 'max_length': 200},
    'slug': {'type': str, 'required': True, 'unique': True},
    'content': {'type': str, 'required': True},
    'excerpt': {'type': str, 'max_length': 500},
    'author': {'type': 'ObjectId', 'ref': 'User', 'required': True},
    'category': {'type': 'ObjectId', 'ref': 'Category'},
    'tags': [str],
    'featured_image': str,
    'status': {'type': str, 'enum': ['draft', 'published', 'archived'], 'default': 'draft'},
    'meta': {
        'views': {'type': int, 'default': 0},
        'likes': {'type': int, 'default': 0},
        'comments_count': {'type': int, 'default': 0}
    },
    'seo': {
        'meta_title': str,
        'meta_description': str,