from flask import Flask, render_template

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('hakctuesx-firebase-adminsdk-2u8as-2928acf840.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)

db = firestore.client()

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def hello_world():
    doc_ref = db.collection(u'users').document(u'students')
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'class': u'G'
    })
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

