from app import db, bcrypt
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def save(self):
        db.users.insert_one({'email': self.email, 'password': self.password})

    @staticmethod
    def find_by_email(email):
        return db.users.find_one({'email': email})

    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)
