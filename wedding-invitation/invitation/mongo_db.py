import pymongo
import hashlib
from datetime import datetime

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


def get_setting(key, default=None):
    try:
        db = get_db()
        doc = db.settings.find_one({'key': key})
        return doc['value'] if doc else default
    except Exception:
        return default


def save_setting(key, value):
    try:
        db = get_db()
        db.settings.update_one({'key': key}, {'$set': {'value': value}}, upsert=True)
        return True
    except Exception:
        return False


def create_invitation(slug, groom_name, bride_name, url):
    try:
        db = get_db()
        db.invitations.update_one(
            {'slug': slug},
            {'$set': {
                'slug': slug,
                'groom_name': groom_name,
                'bride_name': bride_name,
                'url': url,
                'updated_at': datetime.utcnow(),
            }},
            upsert=True,
        )
        return True
    except Exception:
        return False


def get_invitation(slug):
    try:
        db = get_db()
        return db.invitations.find_one({'slug': slug}, {'_id': 0})
    except Exception:
        return None


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
