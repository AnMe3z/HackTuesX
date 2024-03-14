from flask import Flask, render_template, request, redirect, url_for
#real time
import pyrebase
#firestore
import firebase_admin
from firebase_admin import credentials, firestore

#pyrebase / realtime
config = {
"apiKey": "AIzaSyDY4DLLc_fhTTNqdgpVtRRempnbJzxzob4",
  "authDomain": "hakctuesx.firebaseapp.com",
  "projectId": "hakctuesx",
  "storageBucket": "hakctuesx.appspot.com",
  "messagingSenderId": "618046381097",
  "appId": "1:618046381097:web:8a02d3cc92838e983cd038",
  "measurementId": "G-K4JXRH34LB",

    "databaseURL": "https://hakctuesx-default-rtdb.firebaseio.com/"
}

#real time database
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
data = {"name": "John Doe", "email": "johndoe@example.com"}
db.push(data)

#firestore database
cred = credentials.Certificate("hakctuesx-firebase-adminsdk-2u8as-2928acf840.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
#write to firestore database
doc_ref = db.collection(u'users').document(u'students')
doc_ref.set({
    u'first': u'Kur',
    u'last': u'Lovelace',
    u'class': u'G'
})

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except:
            return "Invalid email or password"
    return render_template('login.html')

@app.route('/home')
def home():
    return "You are logged in"

if __name__ == '__main__':
    app.run(debug=True)

