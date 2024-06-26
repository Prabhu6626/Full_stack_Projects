from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, login_manager, mail
from models import User
from flask_mail import Message
from bson.objectid import ObjectId

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(email=user_data['email'], password=user_data['password'], _id=user_data['_id'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.find_by_email(email):
            flash('Email address already exists')
            return redirect(url_for('register'))
        user = User(email, password)
        user.save()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = User.find_by_email(email)
        if user_data and User.check_password(user_data.password, password):
            user = User(email=user_data.email, password=user_data.password, _id=user_data.id)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        description = request.form['description']
        db.events.insert_one({'name': name, 'date': date, 'description': description, 'organizer': current_user.email})
        flash('Event created successfully')
        return redirect(url_for('dashboard'))
    return render_template('create_event.html')
