from flask import Flask, render_template, request, redirect, url_for, session
import json

from datetime import datetime

import calendar
from calendar_helper import generate_calendar_data

from firebase import firebase

app = Flask(__name__)
app.secret_key = 'mlqsqQ1PXL55EhfWEzTl9BBaMr4qy5'  # Set your secret key here

firebase = firebase.FirebaseApplication('https://hakctuesx-default-rtdb.firebaseio.com/', None)

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
@app.route('/chat')

def chat():
    # Retrieve chat messages from Firebase
    messages = firebase.get('/chat/messages', None)
    if messages is None:
        messages = []
    else:
        messages = [{'user': message['user'], 'message': message['message']} for message in messages.values()]

    # Pass messages to the template and render the chat page
    return render_template('chat.html', messages=messages)

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

        # Fetch user credentials from Firebase
        user_data = firebase.get('/users/' + username, None)

        if user_data is not None and password == user_data['password']:
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
        tasks_data = firebase.get('/tasks', None)
        tasks = []

        if tasks_data:
            for task_id, task_info in tasks_data.items():
                task_info['id'] = task_id
                tasks.append(task_info)

        # Fetch chat messages from Firebase
        messages_data = firebase.get('/chat/messages', None)
        messages = []

        if messages_data:
            for message_id, message_info in messages_data.items():
                messages.append({'user': message_info['user'], 'message': message_info['message']})

        # Get user information from Firebase
        current_user = session['user']
        user_info = firebase.get('/users', current_user)
        user_type = user_info.get('user_type')

        # Generate calendar data
        calendar_data = generate_calendar_data(tasks)

        return render_template('dashboard.html', tasks=tasks, user_type=user_type, calendar=calendar_data, current_user=current_user, messages=messages)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST', 'GET'])
def add_task():
    if 'user' in session:
        task_name = request.form['task_name']  # Retrieve task name from the form
        task_description = request.form['description']
        task_deadline = request.form['deadline']
        assignee = request.form['assignee']
        creator = session['user']

        # Add task to Firebase with all attributes
        new_task_ref = firebase.post('/tasks', {
            'task_name': task_name,
            'description': task_description,
            'deadline': task_deadline,
            'assignee': assignee,
            'creator': creator
        })

        return redirect(url_for('dashboard'))
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

@app.route('/heads')
def heads():
    heads_data = firebase.get('/heads', None)
    heads_list = []
    if heads_data:
        for head, status in heads_data.items():
            heads_list.append({'name': head, 'status': status})

    return render_template('heads.html', heads=heads_list)

@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']

    # Write user information to Firebase
    firebase.put('/users', username, {'password': password, 'user_type': user_type})

    return "User registered successfully."

@app.route('/edit_profile')
def edit_profile():
    if 'user' in session:
        username = session['user']
        user_info = firebase.get('/users', username)

        if user_info is not None:
            return render_template('edit_profile.html', user_info=user_info)
        else:
            # Handle the case where user_info is None (e.g., user not found)
            return "User information not found."
    else:
        return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' in session:
        username = session['user']
        user_info = firebase.get('/users', None)

        # Retrieve updated profile data from the form
        new_password = request.form['password']
        new_user_type = request.form['user_type']

        # Update user data in Firebase
        if user_info and username in user_info:
            updated_user_info = {
                'password': new_password,
                'user_type': new_user_type
            }
            firebase.patch('/users/' + username, updated_user_info)

            return redirect(url_for('dashboard'))
        else:
            return "User not found in database."
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)