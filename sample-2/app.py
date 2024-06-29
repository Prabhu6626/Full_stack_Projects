from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'secret'

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/event-management'
mongo = PyMongo(app)
events_collection = mongo.db.events
users_collection = mongo.db.users

# Routes

@app.route('/')
def index():
    events = list(events_collection.find())
    return render_template('index.html', events=events)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        users_collection.insert_one({
            'username': username,
            'password': password,
            'role': role
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return 'Invalid username/password combination'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        ticket_limit = int(request.form['ticket_limit'])
        events_collection.insert_one({
            'event_name': event_name,
            'event_date': event_date,
            'ticket_limit': ticket_limit,
            'booked_users': []  # Initialize as empty list
        })
        return redirect(url_for('index'))
    return render_template('create_event.html')

@app.route('/book/<event_id>', methods=['POST'])
def book(event_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    event = events_collection.find_one({'_id': ObjectId(event_id)})
    if not event:
        return 'Event not found'

    if session['role'] == 'customer':
        # Check if tickets are available
        if len(event['booked_users']) < event['ticket_limit']:
            # Add the current user to booked users
            event['booked_users'].append(session['username'])
            events_collection.update_one({'_id': ObjectId(event_id)}, {'$set': {'booked_users': event['booked_users']}})
            return redirect(url_for('index'))
        else:
            return 'Ticket limit reached for this event'

    return 'Unauthorized'

@app.route('/attendance/<event_id>')
def attendance(event_id):
    if 'username' not in session or session['role'] != 'event_creator':
        return redirect(url_for('login'))

    event = events_collection.find_one({'_id': ObjectId(event_id)})
    if not event:
        return 'Event not found'

    booked_users = event['booked_users']
    return render_template('attendance.html', event=event, booked_users=booked_users)

if __name__ == '__main__':
    app.run(debug=True)
