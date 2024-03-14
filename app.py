from flask import Flask, render_template, request, redirect, url_for, session
import json

from datetime import datetime

import calendar
from calendar_helper import generate_calendar_data

from firebase import firebase

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '123'  # Set your secret key here

# Initialize Firebase app
firebase = firebase.FirebaseApplication('https://hakctuesx-default-rtdb.firebaseio.com/', None)

# Routes
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded accounts
        accounts = {
            'student': 'student',
            'head': 'head',
            'admin': 'admin'
        }

        # Check if the provided credentials match any of the hardcoded accounts
        if username in accounts and password == accounts[username]:
            # Authentication successful
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            # Authentication failed
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        # Fetch tasks from Firebase
        tasks = firebase.get('/tasks', None)

        if tasks is None:
            tasks = []
        else:
            tasks = tasks.values()

        # Fetch chat messages from Firebase
        messages = firebase.get('/chat/messages', None)
        if messages is None:
            messages = []
        else:
            messages = [{'user': message['user'], 'message': message['message']} for message in messages.values()]

        # Get the current user from the session
        current_user = session['user']

        # Generate calendar data
        calendar_data = generate_calendar_data(tasks)

        return render_template('dashboard.html', tasks=tasks, calendar=calendar_data, current_user=current_user, messages=messages)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user' in session:
        task_description = request.form['task']
        task_deadline = request.form['deadline']
        assignee = request.form['assignee']
        creator = session['user']

        # Check if the current user has the privilege to assign tasks
        # You can replace this condition with your specific logic
        if creator == 'admin' or creator == 'head':
            # Add task to Firebase with creator and assignee
            new_task_ref = firebase.post('/tasks', {
                'description': task_description,
                'deadline': task_deadline,
                'creator': creator,
                'assignee': assignee
            })

            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', error='You do not have permission to assign tasks'))
    else:
        return redirect(url_for('login'))

@app.route('/clear_tasks', methods=['POST'])
def clear_tasks():
    if 'user' in session:
        # Delete all tasks from Firebase
        firebase.delete('/tasks', None)

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' in session:
        username = session['user']
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Push the message to Firebase
        new_message_ref = firebase.post('/chat/messages', {'user': username, 'message': message, 'timestamp': timestamp})

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
