from app import db, bcrypt
from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self.id = str(_id) if _id else None

    def save(self):
        user_id = db.users.insert_one({'email': self.email, 'password': self.password}).inserted_id
        self.id = str(user_id)

    @staticmethod
    def find_by_email(email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(email=user_data['email'], password=user_data['password'], _id=user_data['_id'])
        return None

    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)

    def get_id(self):
        return self.id
