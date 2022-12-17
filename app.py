from flask import Flask, render_template, redirect, request, session, flash, g
from datetime import timedelta
import sqlite3
import re


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
		db.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, email TEXT, password TEXT)""")
		db.execute("""CREATE TABLE IF NOT EXISTS courses(course_id INTEGER PRIMARY KEY,
			user_id INTEGER, course_name TEXT, lesson INTEGER, 
			FOREIGN KEY(user_id) REFERENCES users(user_id))""")

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
		
		userEmail = request.form["email"]
		userPassword = request.form["password"]
		db, connection = get_db()
		db.execute('SELECT user_id FROM users WHERE email=? AND password = ?', (userEmail, userPassword))
		user_id = db.fetchall() # returns a tuple like this: (userId,)
		if user_id: # if user exists
			session.permanent = True
			session["user_id"] = user_id[0]
			session["email"] = userEmail
			session["password"] = userPassword
			flash(f"You have been logged in {userEmail}")
			return redirect("dashboard")

		else: #if user doesn't exist
			flash("Email or Password is Incorrect. Try Again")
			return redirect("login")

	else: #got there via GET
		if "email" in session: # if user is already logged in and they get here through GET
			flash("Already logged in")
			return redirect("dashboard")
		return render_template("login.html") # if user isn't logged in and gets here via GET



@app.route("/signup", methods = ["POST", "GET"])
def signup():
	if request.method == "POST": #user submitted sign up sheet
		session.permanent = True
		userEmail = request.form["email"]
		userPassword = request.form["password"]
		validEmail = re.search(r".+@.+\.", userEmail)

		#email has good format
		if validEmail:
			db, connection = get_db()
			db.execute('SELECT user_id FROM users WHERE email=?', (userEmail,))
			userExists = db.fetchall()
			flash(f"user_id: {userExists}")

			#check if email already exists
			if not userExists:
				db.execute("INSERT INTO users(email, password) VALUES(?, ?)", (userEmail, userPassword))
				connection.commit()

				db.execute("SELECT user_id FROM users WHERE email = ?", (userEmail,))
				user_id = db.fetchall()
				session["user_id"] = user_id[0]
				session["email"] = userEmail
				session["password"] = userPassword

				flash("You have been signed up")
				return redirect("dashboard")
			#if email already exists
			else:
				flash("An account with the same email already exists")
				return redirect("signup")

		#email has bad format
		else:
			flash("Email is incorrectly formatted")
			return redirect("signup")

	else: #got there via GET
		if "email" in session: # if user is already logged in and they get here through GET
			flash("Already logged in")
			return redirect("dashboard")

		return render_template("signup.html")  # if user isn't logged in and gets here via GET
		
'''
	1. Users who are logged in will see a personalized dashboard
	2. Users who are not logged in will be redirected to the login page (gotta fix the flash)
'''
@app.route("/dashboard")
def dashboard():
	if "user_id" in session: # say hi via personalized email (if logged in)
		user_id = session["user_id"]
		userEmail = session["email"]
		db, connection = get_db()
		db.execute("SELECT course_id, course_name, lesson FROM courses WHERE user_id = ?", (user_id))
		courseList = db.fetchall()
		return render_template("dashboard.html", email = userEmail, courses = courseList)
	
	else:
		flash("you are not logged in")
		return redirect("login")


#for testing session length; to be implemented better in the future
@app.route("/logout")
def logout():
	flash("You have been logged out!", "info")
	session.pop("user_id", None)
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
