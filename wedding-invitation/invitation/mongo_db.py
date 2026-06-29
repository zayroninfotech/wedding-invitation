import pymongo
import hashlib

MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME   = 'wedding_vamsi_anausha'

_client = None

def get_db():
    global _client
    if _client is None:
        _client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client[DB_NAME]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(username: str, password: str) -> bool:
    try:
        db = get_db()
        user = db.users.find_one({'username': username.strip().lower()})
        if user and user.get('password_hash') == hash_password(password):
            return True
        return False
    except Exception:
        return False


def seed_superadmin():
    """Insert superadmin if not already present."""
    try:
        db = get_db()
        if not db.users.find_one({'username': 'vamsi'}):
            db.users.insert_one({
                'username': 'vamsi',
                'password_hash': hash_password('zayron@2026'),
                'role': 'superadmin',
            })
            print('[MongoDB] Superadmin user created.')
        else:
            print('[MongoDB] Superadmin already exists.')
    except Exception as e:
        print(f'[MongoDB] Warning: {e}')
