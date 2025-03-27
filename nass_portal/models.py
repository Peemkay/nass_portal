from flask_login import UserMixin
from .db import get_db

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        db = get_db()
        user = db.execute('SELECT * FROM admins WHERE id = ?', (user_id,)).fetchone()
        if user:
            return User(user['id'], user['username'])
        return None
