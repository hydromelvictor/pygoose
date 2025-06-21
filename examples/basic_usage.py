"""Exemple de base pour tester PyMongoose"""

from pygoose import connect, Schema, model
from datetime import datetime

# 1. Connexion à MongoDB
connect('mongodb://localhost:27017/test_pymongoose')

# 2. Définition des schémas
UserSchema = Schema({
    'username': {'type': str, 'required': True, 'unique': True, 'min_length': 3},
    'email': {'type': str, 'required': True, 'unique': True, 'validate': 'email'},
    'password': {'type': str, 'required': True, 'min_length': 6},
    'age': {'type': int, 'min': 13, 'max': 120},
    'profile': {
        'first_name': str,
        'last_name': str,
        'bio': str,
        'avatar': str
    },
    'preferences': {
        'theme': {'type': str, 'enum': ['light', 'dark'], 'default': 'light'},
        'notifications': {'type': bool, 'default': True}
    },
    'tags': [str],  # Array de strings
    'is_active': {'type': bool, 'default': True},
    'last_login': 'datetime'
}, {
    'timestamps': True,  # Ajoute created_at et updated_at
    'collection': 'users'
})

# Hook pré-sauvegarde pour hasher le mot de passe
@UserSchema.pre('save')
def hash_password(doc):
    if doc.is_modified('password'):
        # Ici vous ajouteriez le hashage réel
        print(f"Hashage du mot de passe pour {doc.username}")

# Hook post-sauvegarde pour envoyer un email de bienvenue
@UserSchema.post('save')
def send_welcome_email(doc):
    if doc._is_new:
        print(f"Email de bienvenue envoyé à {doc.email}")

# Méthode personnalisée
def get_full_name(self):
    if self.profile and self.profile.get('first_name') and self.profile.get('last_name'):
        return f"{self.profile['first_name']} {self.profile['last_name']}"
    return self.username

UserSchema.method('get_full_name', get_full_name)

# 3. Création du modèle
User = model('User', UserSchema)

# 4. Utilisation

def test_basic_operations():
    print("=== Test des opérations de base ===")
    
    # Créer un utilisateur
    user_data = {
        'username': 'alice123',
        'email': 'alice@example.com',
        'password': 'motdepasse123',
        'age': 25,
        'profile': {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'bio': 'Développeuse Python passionnée'
        },
        'tags': ['python', 'mongodb', 'web'],
        'preferences': {
            'theme': 'dark',
            'notifications': False
        }
    }
    
    try:
        # Méthode 1: Créer et sauvegarder
        user = User(user_data)
        user.save()
        print(f"✓ Utilisateur créé: {user.username} (ID: {user._id})")
        print(f"  Nom complet: {user.get_full_name()}")
        
        # Méthode 2: Créer directement
        user2 = User.create({
            'username': 'bob456',
            'email': 'bob@example.com',
            'password': 'autremotsdepass',
            'age': 30,
            'profile': {
                'first_name': 'Bob',
                'last_name': 'Smith'
            }
        })
        print(f"✓ Utilisateur créé directement: {user2.username}")
        
    except Exception as e:
        print(f"✗ Erreur lors de la création: {e}")

def test_queries():
    print("\n=== Test des requêtes ===")
    
    try:
        # Trouver tous les utilisateurs
        all_users = User.find().exec()
        print(f"✓ Trouvé {len(all_users)} utilisateurs")
        
        # Trouver avec filtre
        active_users = User.find({'is_active': True}).exec()
        print(f"✓ Trouvé {len(active_users)} utilisateurs actifs")
        
        # Trouver un utilisateur par email
        user = User.find_one({'email': 'alice@example.com'})
        if user:
            print(f"✓ Utilisateur trouvé: {user.username}")
            
            # Modifier l'utilisateur
            user.age = 26
            user.last_login = datetime.now()
            user.save()
            print(f"✓ Utilisateur mis à jour: âge = {user.age}")
        
        # Requête avec tri et limite
        recent_users = User.find().sort('-created_at').limit(5).exec()
        print(f"✓ 5 utilisateurs les plus récents récupérés")
        
        # Compter
        count = User.count({'age': {'$gte': 18}})
        print(f"✓ {count} utilisateurs majeurs")
        
    except Exception as e:
        print(f"✗ Erreur lors des requêtes: {e}")

def test_validation():
    print("\n=== Test de validation ===")
    
    # Test validation email
    try:
        invalid_user = User({
            'username': 'test',
            'email': 'email_invalide',  # Email invalide
            'password': '123456'
        })
        invalid_user.save()
        print("✗ La validation email devrait échouer")
    except Exception as e:
        print(f"✓ Validation email échoue correctement: {e}")
    
    # Test champ requis
    try:
        incomplete_user = User({
            'username': 'test2'
            # email et password manquants
        })
        incomplete_user.save()
        print("✗ La validation des champs requis devrait échouer")
    except Exception as e:
        print(f"✓ Validation champs requis échoue correctement: {e}")
    
    # Test contraintes de longueur
    try:
        short_password_user = User({
            'username': 'test3',
            'email': 'test3@example.com',
            'password': '123'  # Trop court
        })
        short_password_user.save()
        print("✗ La validation longueur mot de passe devrait échouer")
    except Exception as e:
        print(f"✓ Validation longueur mot de passe échoue correctement: {e}")

def test_updates_and_deletes():
    print("\n=== Test mises à jour et suppressions ===")
    
    try:
        # Créer un utilisateur de test
        test_user = User.create({
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        print(f"✓ Utilisateur de test créé: {test_user.username}")
        
        # Mise à jour avec Model.update_one
        User.update_one(
            {'username': 'testuser'},
            {'$set': {'age': 22, 'is_active': False}}
        )
        
        # Vérifier la mise à jour
        updated_user = User.find_one({'username': 'testuser'})
        print(f"✓ Utilisateur mis à jour: âge = {updated_user.age}, actif = {updated_user.is_active}")
        
        # Suppression
        updated_user.delete()
        print("✓ Utilisateur supprimé")
        
        # Vérifier la suppression
        deleted_user = User.find_one({'username': 'testuser'})
        if not deleted_user:
            print("✓ Suppression confirmée")
        
    except Exception as e:
        print(f"✗ Erreur lors des mises à jour/suppressions: {e}")

if __name__ == "__main__":
    test_basic_operations()
    test_queries()
    test_validation()
    test_updates_and_deletes()
    print("\n=== Tests terminés ===")