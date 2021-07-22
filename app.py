import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# app configure
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# rendering home page
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

# rendering player plans page and accessing plans data collection
@app.route("/player_plans")
def player_plans():
    plans = mongo.db.plans.find()
    return render_template("plans.html", plans=plans)

#rendering legends page and accessing legends data collection
@app.route("/get_legends")
def get_legends():
    legends = mongo.db.legends.find()
    return render_template("legends.html", legends=legends)

# rendering register page and registering new users
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email")
        }
        mongo.db.users.insert_one(register)

        # put new user into 'session'
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")

# rendering maps page and accessing maps data collection
@app.route("/get_maps")
def get_maps():
    maps = mongo.db.maps.find()
    return render_template("maps.html", maps=maps)

# rendering login page and logging in users
@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        #checking if user exists
        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Hello, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for('log_in'))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for('log_in'))

    return render_template("login.html")

#rendering profile page and accessing users data collection 
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))

# log out functionality
@app.route("/log_out")
def log_out():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("log_in"))

#rendering add plan page and allowing users to insert data to the collection
@app.route("/add_plan", methods=["GET", "POST"])
def add_plan():
    if request.method == "POST":
        plan = {
            "plan_type": request.form.get("plan_type"),
            "plan_aim": request.form.get("plan_aim"),
            "created_by": session["user"]
        }
        mongo.db.plans.insert_one(plan)
        flash("Plan added!")
        return redirect(url_for("player_plans"))

    return render_template("add-plan.html")

#render edit plan page and allow user to change data in plans collection
@app.route("/edit_plan/<plan_id>", methods=["GET", "POST"])
def edit_plan(plan_id):
    if request.method == "POST":
        submit = {
            "plan_type": request.form.get("plan_type"),
            "plan_aim": request.form.get("plan_aim"),
            "created_by": session["user"]
        }
        mongo.db.plans.update({"_id": ObjectId(plan_id)}, submit)
        flash("Plan Updated!")
        return redirect(url_for("player_plans"))

    plan = mongo.db.plans.find_one({"_id": ObjectId(plan_id)})
    return render_template("edit-plan.html", plan=plan)

#plan deletion functionality
@app.route("/delete_plan/<plan_id>")
def delete_plan(plan_id):
    mongo.db.plans.remove({"_id": ObjectId(plan_id)})
    flash("Plan Deleted!")
    return redirect(url_for("player_plans"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
