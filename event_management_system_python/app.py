from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/event_management"

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

EVENTS_JSON_FILE = 'events.json'

class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.check_password_hash(hashed_password, password)

    @staticmethod
    def get_user(email):
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return User(str(user_data['_id']), user_data['email'], user_data['password'])
        return None

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data['_id']), user_data['email'], user_data['password'])
    return None

def save_event_to_json(event_data):
    if os.path.exists(EVENTS_JSON_FILE):
        with open(EVENTS_JSON_FILE, 'r') as file:
            events = json.load(file)
    else:
        events = []

    events.append(event_data)
    
    with open(EVENTS_JSON_FILE, 'w') as file:
        json.dump(events, file, indent=4)

def read_events_from_json():
    if os.path.exists(EVENTS_JSON_FILE):
        with open(EVENTS_JSON_FILE, 'r') as file:
            return json.load(file)
    return []

@app.route('/')
def index():
    events = list(mongo.db.events.find())
    json_events = read_events_from_json()
    return render_template('index.html', events=events + json_events)

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        name = request.form.get('name')
        date = request.form.get('date')
        description = request.form.get('description')
        tickets_available = request.form.get('tickets_available')

        if not name or not date or not description or not tickets_available:
            flash('Please enter all the fields', 'error')
            return redirect(url_for('create_event'))

        event_data = {
            'name': name,
            'date': date,
            'description': description,
            'tickets_available': tickets_available,
            'created_by': current_user.id
        }

        mongo.db.events.insert_one(event_data)
        save_event_to_json(event_data)

        flash('Event created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_event.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            'email': email,
            'password': hashed_password
        }

        mongo.db.users.insert_one(user_data)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_user(email)
        
        if user and User.check_password(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
