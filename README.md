# 🚀 PyMongoose - Guide Rapide

## Installation Ultra-Rapide

```bash
pip install pygoose
```

## ⚡ Démarrage en 30 Secondes

```python
from pygoose import connect, Schema, model

# 1. Connexion (une seule ligne)
connect('mongodb://localhost:27017/myapp')

# 2. Définir un schéma
UserSchema = Schema({
    'name': str,
    'email': str,
    'age': int,
    'created_at': {'type': 'datetime', 'default': 'now'}
})

# 3. Créer un modèle
User = model('User', UserSchema)

# 4. Utiliser !
user = User(name="Alice", email="alice@example.com", age=25)
user.save()
```

## 🎯 Concepts Clés (5 minutes)

### 1. **Schema** = Structure de vos données

```python
# Simple
UserSchema = Schema({
    'name': str,
    'email': str
})

# Avec validation
UserSchema = Schema({
    'name': {'type': str, 'required': True, 'min_length': 2},
    'email': {'type': str, 'required': True, 'unique': True},
    'age': {'type': int, 'min': 0, 'max': 120},
    'tags': [str],  # Array de strings
    'profile': {    # Objet imbriqué
        'bio': str,
        'avatar': str
    }
})
```

### 2. **Model** = Interface pour vos données

```python
User = model('User', UserSchema)
```

### 3. **Document** = Une instance de vos données

```python
user = User(name="Bob", email="bob@example.com")
```

## 🔥 Opérations Essentielles

### **Créer (Create)**

```python
# Méthode 1 : Instancier puis sauvegarder
user = User(name="Alice", email="alice@example.com")
user.save()

# Méthode 2 : Créer directement
user = User.create(name="Bob", email="bob@example.com")

# Méthode 3 : Créer plusieurs
users = User.create_many([
    {'name': 'Charlie', 'email': 'charlie@example.com'},
    {'name': 'David', 'email': 'david@example.com'}
])
```

### **Lire (Read)**

```python
# Trouver tous
users = User.find()

# Trouver avec conditions
users = User.find({'age': {'$gte': 18}})

# Trouver un seul
user = User.find_one({'email': 'alice@example.com'})

# Par ID
user = User.find_by_id('507f1f77bcf86cd799439011')

# Avec méthodes chainées
users = User.find({'age': {'$gte': 18}}).sort('name').limit(10)
```

### **Mettre à jour (Update)**

```python
# Mise à jour d'un document
user = User.find_one({'email': 'alice@example.com'})
user.age = 26
user.save()

# Mise à jour directe
User.update_one({'email': 'alice@example.com'}, {'$set': {'age': 26}})

# Mise à jour multiple
User.update_many({'age': {'$lt': 18}}, {'$set': {'category': 'minor'}})
```

### **Supprimer (Delete)**

```python
# Supprimer un document
user = User.find_one({'email': 'alice@example.com'})
user.delete()

# Supprimer directement
User.delete_one({'email': 'alice@example.com'})

# Supprimer plusieurs
User.delete_many({'age': {'$lt': 13}})
```

## 🎨 Types de Champs Simplifiés

```python
# Types de base
Schema({
    'text': str,                    # String
    'number': int,                  # Integer
    'price': float,                 # Float
    'active': bool,                 # Boolean
    'birthday': 'datetime',         # Date/DateTime
    'data': dict,                   # Object/Dict
    'tags': [str],                  # Array
    'user_id': 'ObjectId'           # Référence MongoDB
})

# Avec validation
Schema({
    'email': {
        'type': str,
        'required': True,
        'unique': True,
        'validate': 'email'         # Validation email intégrée
    },
    'age': {
        'type': int,
        'min': 0,
        'max': 120,
        'default': 18
    },
    'status': {
        'type': str,
        'enum': ['active', 'inactive', 'pending']
    }
})
```

## 🔗 Relations (Références)

```python
# Schéma avec référence
PostSchema = Schema({
    'title': str,
    'content': str,
    'author': {'type': 'ObjectId', 'ref': 'User'},  # Référence vers User
    'tags': [{'type': 'ObjectId', 'ref': 'Tag'}]    # Array de références
})

Post = model('Post', PostSchema)

# Créer avec référence
post = Post.create({
    'title': 'Mon Article',
    'content': 'Contenu...',
    'author': user._id  # ID de l'utilisateur
})

# Populate (charger les références)
post = Post.find_one({'title': 'Mon Article'}).populate('author')
print(post.author.name)  # Accès direct aux données de l'utilisateur
```

## 🎪 Hooks/Middleware

```python
# Avant sauvegarde
@UserSchema.pre('save')
def hash_password(doc):
    if doc.is_modified('password'):
        doc.password = hash_password(doc.password)

# Après sauvegarde
@UserSchema.post('save')
def send_welcome_email(doc):
    send_email(doc.email, 'Bienvenue!')

# Avant suppression
@UserSchema.pre('delete')
def cleanup_user_data(doc):
    # Nettoyer les données associées
    Post.delete_many({'author': doc._id})
```

## 🔍 Requêtes Avancées Simplifiées

```python
# Recherche texte
users = User.find({'$text': {'$search': 'alice'}})

# Regex
users = User.find({'name': {'$regex': '^A', '$options': 'i'}})

# Plage de dates
from datetime import datetime, timedelta
last_week = datetime.now() - timedelta(days=7)
users = User.find({'created_at': {'$gte': last_week}})

# Tri et pagination
users = User.find().sort('-created_at').skip(20).limit(10)

# Projection (sélectionner certains champs)
users = User.find({}, {'name': 1, 'email': 1})

# Aggregation simple
pipeline = [
    {'$match': {'age': {'$gte': 18}}},
    {'$group': {'_id': '$city', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]
result = User.aggregate(pipeline)
```

## ⚙️ Configuration Avancée

```python
# Connexion avec options
connect('mongodb://localhost:27017/myapp', {
    'maxPoolSize': 50,
    'minPoolSize': 5,
    'serverSelectionTimeoutMS': 5000,
    'socketTimeoutMS': 5000,
})

# Schéma avec options
UserSchema = Schema({
    'name': str,
    'email': str
}, {
    'collection': 'users',         # Nom de collection personnalisé
    'timestamps': True,            # Ajoute created_at et updated_at
    'strict': False,               # Permet champs non définis
    'validate_before_save': True   # Validation automatique
})
```

## 🔧 Validation Personnalisée

```python
def validate_phone(value):
    import re
    if not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValueError('Numéro de téléphone invalide')
    return value

UserSchema = Schema({
    'phone': {
        'type': str,
        'validate': validate_phone
    }
})
```

## 🚨 Gestion d'Erreurs

```python
from pygoose.exceptions import ValidationError, NotFoundError

try:
    user = User.create({'name': 'Test'})  # Email requis manquant
except ValidationError as e:
    print(f"Erreur de validation: {e}")

try:
    user = User.find_by_id('invalid_id')
except NotFoundError:
    print("Utilisateur non trouvé")
```

## 🎯 Patterns Courants

### 1. **Modèle Utilisateur Complet**

```python
UserSchema = Schema({
    'email': {'type': str, 'required': True, 'unique': True, 'validate': 'email'},
    'password': {'type': str, 'required': True, 'min_length': 6},
    'profile': {
        'first_name': str,
        'last_name': str,
        'avatar': str,
        'bio': str
    },
    'settings': {
        'notifications': {'type': bool, 'default': True},
        'theme': {'type': str, 'enum': ['light', 'dark'], 'default': 'light'}
    },
    'roles': [{'type': str, 'enum': ['user', 'admin', 'moderator']}],
    'last_login': 'datetime',
    'is_active': {'type': bool, 'default': True}
}, {
    'timestamps': True
})
```

### 2. **Système de Blog**

```python
# Modèle Article
ArticleSchema = Schema({
    'title': {'type': str, 'required': True},
    'slug': {'type': str, 'unique': True},
    'content': {'type': str, 'required': True},
    'excerpt': str,
    'author': {'type': 'ObjectId', 'ref': 'User', 'required': True},
    'categories': [{'type': 'ObjectId', 'ref': 'Category'}],
    'tags': [str],
    'featured_image': str,
    'status': {'type': str, 'enum': ['draft', 'published', 'archived'], 'default': 'draft'},
    'meta': {
        'views': {'type': int, 'default': 0},
        'likes': {'type': int, 'default': 0},
        'comments_count': {'type': int, 'default': 0}
    }
}, {
    'timestamps': True
})

# Auto-génération du slug
@ArticleSchema.pre('save')
def generate_slug(doc):
    if not doc.slug:
        doc.slug = slugify(doc.title)
```

## 🎨 Conseils Pro

1. **Indexation** : Ajoutez des index pour les requêtes fréquentes

```python
UserSchema.index([('email', 1)], unique=True)
UserSchema.index([('created_at', -1)])
```

2. **Validation conditionnelle**

```python
def validate_adult_email(doc):
    if doc.age >= 18 and not doc.email:
        raise ValueError('Email requis pour les adultes')

UserSchema.add_validator(validate_adult_email)
```

3. **Méthodes personnalisées**

```python
def get_full_name(self):
    return f"{self.profile.first_name} {self.profile.last_name}"

UserSchema.add_method('get_full_name', get_full_name)

# Utilisation
user = User.find_one({'email': 'alice@example.com'})
print(user.get_full_name())
```

## 🏃‍♂️ Exemple Complet en 2 Minutes

```python
from pygoose import connect, Schema, model

# Connexion
connect('mongodb://localhost:27017/blog')

# Schémas
UserSchema = Schema({
    'username': {'type': str, 'required': True, 'unique': True},
    'email': {'type': str, 'required': True, 'unique': True},
    'password': {'type': str, 'required': True}
}, {'timestamps': True})

PostSchema = Schema({
    'title': {'type': str, 'required': True},
    'content': {'type': str, 'required': True},
    'author': {'type': 'ObjectId', 'ref': 'User'},
    'published': {'type': bool, 'default': False}
}, {'timestamps': True})

# Modèles
User = model('User', UserSchema)
Post = model('Post', PostSchema)

# Utilisation
user = User.create({
    'username': 'alice',
    'email': 'alice@example.com',
    'password': 'secret123'
})

post = Post.create({
    'title': 'Mon premier article',
    'content': 'Contenu de l\'article...',
    'author': user._id,
    'published': True
})

# Récupération avec populate
post = Post.find_one({'title': 'Mon premier article'}).populate('author')
print(f"Article par {post.author.username}")
```

**Vous êtes prêt ! 🎉**

Cette documentation vous donne 90% de ce dont vous avez besoin pour utiliser Pygoose efficacement. Le framework est conçu pour être intuitif et proche de Mongoose.js tout en restant pythonique.
