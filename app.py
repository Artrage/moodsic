import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# @app.route("/")
# @app.route("/get_albums")
# def get_albums():
#     albums = mongo.db.albums.find()
#     return render_template("albums.html", albums=albums)


@app.route("/")
@app.route("/mood")
def mood():
    mood = mongo.db.albums.find()
    return render_template("mood.html", mood=mood)


@app.route("/")
@app.route("/get_happy")
def get_happy():
    output = []

    happy = mongo.db.albums.find({"mood": "Happy"})
    for h in happy:
        oh = dict()
        oh['spotify'] = h.get('spotify')
        oh['artwork'] = h.get('artwork')
        oh['artist'] = h.get('artist')
        oh['title'] = h.get('title')
        oh['mood'] = h.get('mood')
        oh['genre'] = h.get('genre')
        oh['year'] = h.get('year')
        oh['is_fav'] = h.get('is_fav')
        oh['id'] = h.get('_id')

        oh['comments'] = []

        # step 1: find all comments for album by album._id
        comments = mongo.db.comments.find({"album_id": h.get('_id')})

        print('Comments Count: ' + str(comments.count()))

        # step 2: iterate over each comment
        for c in comments:
            comment_content = c['comment']
            comment_username = c['username']
            oh['comments'] += [
                {
                    'content': comment_content,
                    'username': comment_username
                }
            ]

        output += [oh]

    return render_template("happy.html", happy=output)


# @app.route("/")
# @app.route("/get_happy")
# def get_happy():
#     happy = mongo.db.albums.find({"mood": "Happy"})

#     view_review = mongo.db.comments.find({""})
#     return render_template("happy.html", happy=happy)


# @app.route("/")
# @app.route("/view_review/<album_id>")
# def view_review(album_id):

#     view_review = mongo.db.comments.find_one(
#         {"_id": ObjectId(album_id)}
#     )
    
#     return (view_review=view_review)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already in use. Please choose another")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("You are now totally registered!!!111")

        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("register"))

    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("Logged out. Ciao!")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_review/<album_id>", methods=["GET", "POST"])
def add_review(album_id):

    add_review = mongo.db.albums.find_one(
    {"_id": ObjectId(album_id)})

    if request.method == "POST":
    
        # user_id = mongo.db.users.find_one(
        # {"_id": request.form.get["_id"]})["user_id"]

        review = {
            "comment": request.form.get("comment"),
            "username": session["user"],
            "album_id": ObjectId(album_id),
            # "user_id": ObjectId(user_id)
        }
        mongo.db.comments.insert_one(review)
        flash("Your review has been added!")
        return redirect(url_for("get_happy"))

    if session["user"]:
        return render_template("add_review.html", add_review=add_review)
    else:
        flash("You have to log in to leave a review")
        return redirect(url_for("login"))





if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
