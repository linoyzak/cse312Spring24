from flask import Flask,render_template, make_response, request, flash, redirect, url_for
import bcrypt
from pymongo import MongoClient



app = Flask(__name__)
mongo_client = MongoClient("mongo") 
db = mongo_client["Theranos"] 
users = db["users"]


@app.route('/',methods=["GET"])
def index():
    print("We here")
    return render_template('/index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    return render_template('login.html')

@app.route('/signup', methods=["GET", "POST"])
def singup():
    currmeth = request.method
    if currmeth == "POST":
        username = request.form["username"]
        password = request.form['password']
        salted = bcrypt.hashpw(password, bcrypt.gensalt())

        data = {"username":username,"password":salted}
        users.insert_one(data)
        flash("Account created but it's Jesse's fault.")
        return render_template('login.html')
    return render_template('signup.html')
    



#On deployment change localhost to 0.0.0.0
app.run(port=8080, host='localhost')