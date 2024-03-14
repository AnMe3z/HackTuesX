from flask import Flask, render_template, request, redirect
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/succes')
def good():
   return 'succes'


@app.route('/submit',methods=["POST","GET"])
def submit():
    if(request.method=="POST"):
     f = request.files['file']
     f.save(f.filename)
     return "file saved succesfully"
    else: 
     return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)