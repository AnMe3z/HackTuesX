from flask import Flask, render_template, request, redirect, url_for
import pyrebase

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

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
#real time database
db = firebase.database()
data = {"name": "John Doe", "email": "johndoe@example.com"}
db.push(data)

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

