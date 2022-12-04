from flask import Flask, render_template, redirect, request, session, flash, g
from datetime import timedelta
import sqlite3


app = Flask(__name__)
app.secret_key = "Testing"
app.permanent_session_lifetime = timedelta(seconds = 30)

'''
	1. Get the connection and db object so we can db.execute & connection.commit from any route
	2. g is a global object where you can store data and access it from anywhere in the app 
'''
def get_db():
	connection = getattr(g, '_database', None)
	if connection is None: # open database if no database is active
		connection = g._database = sqlite3.connect('users.db')
		db = connection.cursor()
		db.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, email TEXT, password TEXT)""")
		connection.commit()
	return db, connection

#Close the database to avoid leaking memory
@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None: #close if there is a database
		db.close()

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("aboutus.html")


@app.route("/programs")
def programs():
	return render_template("programs.html")

'''
	1. User submits form via POST & new account is created (transfer this to sign up)
	2. User that is signed in will be redirected to the dashboard route
	3. User that is not signed in and didn't submit a form will see the normal login page
'''
@app.route("/login", methods = ["POST", "GET"])
def login():

	if request.method == "POST": #submitted login form
		session.permanent = True
		email = request.form["email"]
		password = request.form["password"]
		session["email"] = email
		session["password"] = password
		db, connection = get_db()
		db.execute("INSERT INTO users(email, password) VALUES(?, ?)", (email, password))
		connection.commit()
		flash("You have been logged in")
		return redirect("dashboard")

	else: #got there via GET
		if "email" in session: # if user is already logged in and they get here through GET
			flash("Already logged in")
			return redirect("dashboard")

		return render_template("login.html") # if user isn't logged in and gets here via GET

		
'''
	1. Users who are logged in will see a personalized dashboard
	2. Users who are not logged in will be redirected to the login page (gotta fix the flash)
'''
@app.route("/dashboard")
def dashboard():
	if "email" in session: # say hi via personalized email (if logged in)
		email = session["email"]
		return render_template("dashboard.html", email = email)
	else:
		flash("you are not logged in")
		return redirect("login")


#for testing session length; to be implemented better in the future
@app.route("/logout")
def logout():
	flash("You have been logged out!", "info")
	session.pop("user", None)      #removes the "user" data from the sessions dictionary; None is a msg
	session.pop("email", None)
	return redirect("login")


'''
	1. Shows all of the users who have made an account
'''
@app.route("/users")
def users():
	db, connection = get_db()
	db.execute("SELECT * FROM users")   #This creates a list of tuples; [(col1, col2, col3), {col1, col2, col3)
	userList = db.fetchall()
	return render_template("users.html", users = userList)



if __name__ == '__main__':
	app.run(debug = True)
