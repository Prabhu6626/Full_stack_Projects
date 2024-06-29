from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from app import db

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8') if isinstance(password, str) else password
        self.id = str(_id)

    @staticmethod
    def find_by_email(email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(email=user_data['email'], password=user_data['password'], _id=user_data['_id'])
        return None

    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)

    def save(self):
        user_data = {
            'email': self.email,
            'password': self.password
        }
        result = db.users.insert_one(user_data)
        self.id = str(result.inserted_id)
