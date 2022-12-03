from flask import Flask, render_template, redirect, request, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "Testing"
app.permanent_session_lifetime = timedelta(seconds = 30)



@app.route("/")
def home():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("aboutus.html")


@app.route("/programs")
def programs():
	return render_template("vanish2.html")


@app.route("/login", methods = ["POST", "GET"])
def login():

	if request.method == "POST": #submitted login form
		session.permanent = True
		email = request.form["email"]
		session["email"] = email
		flash("You have been logged in")
		return redirect("dashboard")

	else: #got there via GET
		if "email" in session: # if user is already logged in and they get here through GET
			flash("Already logged in")
			return redirect("dashboard")

		return render_template("login.html") # if user isn't logged in and gets here via GET

		

@app.route("/dashboard")
def dashboard():
	if "email" in session: # say hi via personalized email (if logged in)
		email = session["email"]
		return render_template("dashboard.html", email = email)
	else:
		flash("you are not logged in")
		return render_template("dashboard.html")


#for testing session length; to be implemented better in the future
@app.route("/logout")
def logout():
	flash("You have been logged out!", "info")
	session.pop("user", None)      #removes the "user" data from the sessions dictionary; None is a msg
	session.pop("email", None)
	return redirect("login")


#for testing the program descriptions
@app.route("/vanish")
def vanish():
	return render_template("vanish.html")

if __name__ == '__main__':
	app.run(debug = True)