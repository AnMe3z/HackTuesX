from flask import Flask, render_template, request, redirect, url_for, session
import json

from datetime import datetime

import calendar
from calendar_helper import generate_calendar_data

from firebase import firebase

app = Flask(__name__)
app.secret_key = 'mlqsqQ1PXL55EhfWEzTl9BBaMr4qy5'  # Set your secret key here

firebase = firebase.FirebaseApplication('https://hakctuesx-default-rtdb.firebaseio.com/', None)

@app.route('/send_message', methods=['POST', 'GET'])
def send_message():
    if 'user' in session:
        username = session['user']
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Push the message to Firebase
        new_message_ref = firebase.post('/chat/messages', {'user': username, 'message': message, 'timestamp': timestamp, 'recipient': request.form.get('recipient')})

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/chat', methods=['POST', 'GET'])
def chat():
    # Retrieve chat messages from Firebase
    messages = firebase.get('/chat/messages', None)
    if messages is None:
        messages = []
    else:
        messages = [{'user': message['user'], 'message': message['message'], 'timestamp': message['timestamp'], 'recipient': message['recipient']} for message in messages.values()]

    # Get unique recipients
    recipients = {message['recipient'] for message in messages}

    # Pass messages and recipients to the template and render the chat page
    return render_template('chat.html', messages=messages, recipients=recipients)

@app.route('/')
def index():
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
    return render_template('land.html')
    #if 'user' in session:
        #return redirect(url_for('dashboard'))
    #else:
        #return redirect(url_for('login'))

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
            return render_template('land.html', error='Invalid username or password')

    return render_template('land.html')

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

def populate_available_heads():
    heads = firebase.get('/heads', None)
    available_heads = []

    if heads:
        for head_name, status in heads.items():
            if status == "free":
                available_heads.append(head_name)

    print("Available Heads:", available_heads)
    return available_heads

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        # Retrieve form data
        project_type = request.form.get('project_type')
        head = request.form.get('head')
        theme = request.form.get('theme')
        description = request.form.get('description')

        # Create data dictionary
        project_data = {
            'project_type': project_type,
            'head': head,
            'theme': theme,
            'description': description
        }

        # Save project data to Firebase
        firebase.post('/projects', project_data)
        return redirect(url_for('index'))

    # Populate available heads for the form
    available_heads = populate_available_heads()

    return render_template('createproject.html', available_heads=available_heads)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        link_to_file = request.form.get('link_to_file')
        current_user = session.get('user')  # Get the current user from the session

        if current_user:
            # Get current datetime
            now = datetime.now()
            datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

            data = {
                'link_to_file': link_to_file,
                'current_user': current_user,
                'datetime': datetime_str
            }

            # Push the data to Firebase
            firebase.post('/submissions', data)
    return render_template('submit.html')

@app.route('/success')
def success():
    return "Submission successful! Thank you." 

@app.route('/chat/<conversation_id>', methods=['GET', 'POST'])
def chat_conversation(conversation_id):
    if 'user' in session:
        if request.method == 'POST':
            # Get the message from the form
            message = request.form.get('message')
            if message:
                # Get the current user
                username = session['user']
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Push the message to Firebase under the specified conversation
                firebase.post(f'/chat/{conversation_id}/messages', {'user': username, 'message': message, 'timestamp': timestamp})

        # Retrieve chat messages for the specified conversation from Firebase
        messages_data = firebase.get(f'/chat/{conversation_id}/messages', None)
        messages = []
        if messages_data:
            for message_id, message_info in messages_data.items():
                messages.append({'user': message_info['user'], 'message': message_info['message'], 'timestamp': message_info['timestamp']})

        return render_template('chat_conversation.html', conversation_id=conversation_id, messages=messages)
    else:
        return redirect(url_for('login'))

@app.route('/start_conversation/<recipient>', methods=['GET', 'POST'])
def start_conversation(recipient):
    if 'user' in session:
        if request.method == 'POST':
            # Get the message from the form
            message = request.form.get('message')
            if message:
                # Get the current user
                sender = session['user']
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Create a new conversation ID
                conversation_id = f'{sender}_{recipient}_{timestamp}'

                # Push the message to Firebase under the new conversation ID
                firebase.post(f'/chat/{conversation_id}/messages', {'user': sender, 'message': message, 'timestamp': timestamp})

                # Redirect to the new conversation
                return redirect(url_for('chat_conversation', conversation_id=conversation_id))

        # Render the template for starting a new conversation
        return render_template('start_conversation.html', recipient=recipient)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)