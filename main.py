from flask import Flask, request,render_template
from firebase import firebase


app = Flask(__name__)
import re
def is_google_docs_link(link):
    pattern = r'(https?://)?(www\.)?docs\.google\.com/document/d/[a-zA-Z0-9-_]+'
    return bool(re.match(pattern, link))
firebase = firebase.FirebaseApplication("https://hakctuesx-default-rtdb.firebaseio.com/", None)

@app.route('/upload_link', methods=['POST','GET'])
def upload_link():
    if request.method=='POST':
        link = request.form.get('link')
        if is_google_docs_link(link):
            firebase.post('/files',link)
            return 'fileisintrue'
        else:
            return 'No link has been uploaded'
    elif request.method=='GET':
            return render_template("upload_link.html")

if __name__ == '__main__':
    app.run(debug=True)
