from flask import Flask, request, redirect, url_for, render_template
import pyrebase

config = {
    "apiKey": "AIzaSyDY4DLLc_fhTTNqdgpVtRRempnbJzxzob4",
     "authDomain": "hakctuesx.firebaseapp.com",
    "databaseURL": "https://hakctuesx-default-rtdb.firebaseio.com/",
    "storageBucket": "hakctuesx.appspot.com",
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

app = Flask(__name__)

@app.route('/submit', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        upload = request.files['upload']
        storage.child("files/" + upload.filename).put(upload)

        return redirect(url_for('/'))

    return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)