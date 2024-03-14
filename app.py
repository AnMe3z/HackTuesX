from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    tasks = load_tasks()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    new_task = {
        'description': request.form['task'],
        'deadline': request.form['deadline']
    }
    tasks = load_tasks()
    tasks.append(new_task)
    save_tasks(tasks)
    return redirect(url_for('dashboard'))

def load_tasks():
    try:
        with open('tasks.json', 'r') as f:
            tasks = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        tasks = []
    return tasks

def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f)

if __name__ == '__main__':
    app.run(debug=True)
