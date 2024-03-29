from flask import Flask,render_template, make_response, request, flash, redirect, url_for, session
import bcrypt
from pymongo import MongoClient
import secrets
import hashlib
import uuid
import json



app = Flask(__name__)
mongo_client = MongoClient("mongo") 
db = mongo_client["Theranos"] 
users = db["users"]
tokens = db["tokens"]
posts = db["posts"]
app.secret_key = 'a'
@app.route('/', methods=["GET", "POST"])
def index():
    token = request.cookies.get('token', None)
    if token:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token2 = tokens.find_one({"token_hash": token_hash})
        if token2:
            username = token2['username']
            return render_template('index.html', username=username)
    return render_template('index.html')

@app.route('/styles.css', methods=["GET"])
def style():
    return render_template("/static/css/style.css")
@app.route('/functions.js', methods=["GET"])
def js():
    return render_template("/static/js/functions.js")\
# a
@app.route('/login', methods=["GET", "POST"])
def login():
    currmeth = request.method
    if currmeth == "POST":
        username = request.form["username"]
        password = request.form["password"].encode('utf-8')
        user = users.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password"]) == True:
            session['username'] = user["username"]
            token = secrets.token_urlsafe(16)
            hashed_token = hashlib.sha256(token.encode()).hexdigest()
            tokens.insert_one({"username": username, "token_hash": hashed_token})
            response = make_response(redirect(url_for('index')))
            response.set_cookie('token', token, httponly=True, max_age=3600)  
            return response
    return render_template('index.html')

@app.route('/signup', methods=["POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        user = users.find_one({"username": username})
        if user:
            flash("user already exists!!!!")
            return redirect(url_for('signup_page'))
        password = request.form['password'].encode('utf-8')
        confirm_password = request.form['confirm-password'].encode('utf-8') 
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('signup_page')) 
        salted = bcrypt.hashpw(password, bcrypt.gensalt())
        data = {"email": email, "username":username,"password":salted, "liked_posts":[]}
        users.insert_one(data)
        return render_template('index.html')

@app.route('/signup.html', methods=['GET'])
def signup_page():
    return render_template('signup.html')
    
@app.route('/login.html', methods=['GET'])
def login_p():
    return render_template('login.html')

@app.route('/images.jpeg', methods = ['GET']) 
def render():
    return render_template("/static/images/images.jpeg")

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    username = session.get('username')
    if username != None:
        tokens.delete_one({"username": username})
        session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/feed", methods = ['POST','GET'])
def feed():
    if request.method == 'POST':
        username = session.get('username')
        content = request.form['post_content']
        posts.insert_one({
            'content': content,
            'author': username,
            'likes': 0,
            "likedBy": [],
            "postID": str(uuid.uuid4())
        })
        # print(content)
        all_posts = posts.find()
        return redirect(url_for('feed'))
    else:
        all_posts = posts.find()
        # print(all_posts)
        return render_template('feed.html', posts=all_posts)

@app.route("/like", methods=['POST'])
def likePost():
    # Retrieve the messageId from the request body
    postID = request.json.get('postID')
    # check if post is in user's liked posts database column
    username = session.get("username")
    user = users.find_one({"username": username})
    liked_posts = user.get("liked_posts")
    # if it isnt, increment the post's likes column by 1 and add the post to user's liked posts column
    if postID not in liked_posts:
        posts.update_one({"postID": postID}, {"$inc": {"likes": 1}})
        posts.update_one({"postID": postID}, {"$push": {"likedBy": username}})
        users.update_one({"username": username}, {"$push": {"liked_posts": postID}})

        return redirect(url_for('feed'))
    # else, subtract one like from the post and remove it from user's liked posts data column
    else:
        posts.update_one({"postID": postID}, {"$inc": {"likes": -1}})
        posts.update_one({"postID": postID}, {"$pull": {"likedBy": username}})
        users.update_one({"username": username}, {"$pull": {"liked_posts": postID}})
        return redirect(url_for('feed'))

@app.after_request
def set_response_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response  

if __name__=='__main__':
    app.run(port= 8080, host="0.0.0.0")
#
