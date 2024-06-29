from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
import json
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


app.config['MONGO_URI'] = 'mongodb://localhost:27017/event_manager.users'
mongo = PyMongo(app)
events_collection = mongo.db.events
users_collection = mongo.db.users


@app.route('/')
def index():
    events = load_events()
    return render_template('index.html', events=events)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users_collection = mongo.db.users
        existing_user = users_collection.find_one({'username': request.form['username']})

        if existing_user is None:
            hash_pass = generate_password_hash(request.form['password'])
            users_collection.insert_one({
                'username': request.form['username'],
                'password': hash_pass,
                'role': 'event_creator' if request.form.get('is_creator') else 'customer'
            })
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return 'That username already exists!'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users_collection = mongo.db.users
        login_user = users_collection.find_one({'username': request.form['username']})

        if login_user:
            if check_password_hash(login_user['password'], request.form['password']):
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        return 'Invalid username/password combination'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        events_collection = mongo.db.events
        events_collection.insert_one({
            'event_name': request.form['event_name'],
            'event_date': request.form['event_date'],
            'ticket_limit': int(request.form['ticket_limit']),
            'creator': session['username']
        })
        return redirect(url_for('index'))

    return render_template('create_event.html')

@app.route('/book_event/<event_id>', methods=['POST'])
def book_event(event_id):
    if 'username' not in session:
        return jsonify({'error': 'Login required'}), 401

    events_collection = mongo.db.events
    event = events_collection.find_one({'_id': ObjectId(event_id)})

    if event:
        if event['ticket_limit'] > 0:
            events_collection.update_one(
                {'_id': ObjectId(event_id)},
                {'$inc': {'ticket_limit': -1}}
            )
            return jsonify({'message': 'Ticket booked successfully'})
        else:
            return jsonify({'error': 'Ticket limit exceeded'}), 400

    return jsonify({'error': 'Event not found'}), 404

@app.route('/attendance/<event_id>', methods=['GET'])
def attendance(event_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    events_collection = mongo.db.events
    event = events_collection.find_one({'_id': ObjectId(event_id)})

    if event:
        booked_users = event.get('booked_users', [])
        return render_template('attendance.html', event=event, booked_users=booked_users)

    return 'Event not found'


def load_events():
    events_collection = mongo.db.events
    events = list(events_collection.find())
    return events

if __name__ == '__main__':
    app.run(debug=True)
