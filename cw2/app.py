from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
# to make decorators to work we need to import wraps
from functools import wraps

app = Flask(__name__)



# config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'era1983'
app.config['MYSQL_DB'] = 'bmwforum'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# set MySQL
mysql = MySQL(app)

# home page
@app.route('/')
def index():
	return render_template('home.html')

@app.route('/threads')
def threads():
		# create cursor
		cur = mysql.connection.cursor()

		# get posts
		result = cur.execute("SELECT * FROM threads")

		threads = cur.fetchall()

		if result > 0:
			return render_template('threads.html', threads = threads)
		else:
			msg = "No posts found"
			return render_template('threads.html', msg = msg)
		# close the connection
		cur.close()



@app.route('/thread/<string:id>/')
def thread(id):
		session.pop('thread', None)

		# create cursor
		cur = mysql.connection.cursor()

		# get posts
		cur.execute("SELECT * FROM threads WHERE id = %s", [id])

		thread = cur.fetchone()
		m = str(thread['id'])
		session['thread'] = m

		result = cur.execute("SELECT * FROM posts as p JOIN threads as t ON p.thread_id=t.id WHERE thread_id=%s", (m,))
		rv = cur.fetchall()


		# for testing puposes
		# return '<h1>'+str(thread['id'])+'</h1>'+'<br><p>'+str(rv)+'</p>'
		if result > 0:
			return render_template('posts.html', thread = thread, rv = rv)
		else:
			msg = "No posts found"
			return render_template('posts.html', msg=msg, thread = thread, rv = rv)

		# close the connection
		cur.close()

		return render_template('posts.html', thread = thread, rv = rv)


# register form class
# from the WTForms documentation we have to create a class for each field in the register
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password not match')
	])
	confirm = PasswordField('Confirm Password')

# user register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# cursur creation
		cur = mysql.connection.cursor()

		# execute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		# commit to DB
		mysql.connection.commit()

		# connection close
		cur.close()

		flash('You successfuly registered', 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form=form)

# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# form fields
		username = request.form['username']
		password_user = request.form['password']

		# create the cursor
		cur = mysql.connection.cursor()

		# get user by Username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			# get the stored hash, fetchone is looking at the above query and match the first one found even if are more users with that username
			data = cur.fetchone()
			password = data['password']

			# compaire the passwords
			if sha256_crypt.verify(password_user, password):

				# passed, create our sessions
				session['logged_in'] = True
				session['username'] = username

				# query to set a session id for later usage
				cur.execute('''SELECT * FROM users WHERE username = %s''', (username,))
				rv = cur.fetchone()

				session['usid'] = str(rv['id'])

				# code for testing purposes
				# return '<h1>'+str(rv['id'])+'</h1>'

				flash('Your are now logged in', 'success')
				return redirect(url_for('threads'))
			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)

			# close connection
			cur.close()

		else:
			error = 'Username not found'
			return render_template('login.html', error=error)

	return render_template('login.html')

# check if user logged in
def if_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('You are not authorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap

# logout
@app.route('/logout')
@if_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('threads'))

# dashboard
@app.route('/dashboard')
# used function from above to deny access to this route
@if_logged_in
def dashboard():
	# create cursor
	cur = mysql.connection.cursor()

	# get posts
	result = cur.execute("SELECT * FROM posts")

	posts = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', posts=posts)
	else:
		msg = "No posts found"
		return render_template('dashboard.html', msg=msg)
	# close the connection
	cur.close()

# post form class
class PostForm(Form):
	post = TextAreaField('Post', [validators.Length(min=1)])

# add post
@app.route('/add_post/<string:id>/', methods=['GET', 'POST'])
# used function from above to deny access to this route
@if_logged_in
def add_post(id):
	form = PostForm(request.form)
	if request.method == 'POST' and form.validate():
		post = form.post.data

		# create cursaor
		cur = mysql.connection.cursor()

		# execute
		cur.execute("SELECT * FROM threads WHERE id = %s", [id])
		thread = cur.fetchone()
		m = str(thread['id'])


		cur.execute("INSERT INTO posts (post, user_id, thread_id, author) VALUES (%s, %s, %s, %s)", (post, session['usid'], m,  session['username']))

		# commit to DB
		mysql.connection.commit()

		# close connection
		cur.close()

		flash('Post Created', 'success')

		return redirect(url_for('thread', id=m))
	return render_template('add_post.html', form=form)


# Edit post
@app.route('/edit_post/<string:id>/', methods=['GET', 'POST'])
# used function from above to deny access to this route
@if_logged_in
def edit_post(id):
	# Create cursaor
	cur= mysql.connection.cursor()
	# get post by id
	result = cur.execute("SELECT * FROM posts WHERE id = %s", [id])

	post = cur.fetchone()
	cur.close()


	# Get the form
	form = PostForm(request.form)

	# Populate post form fields
	form.post.data = post['post']

	if request.method == 'POST' and form.validate():
		post = request.form['post']

		# create cursaor
		cur = mysql.connection.cursor()

		# execute
		# cur.execute("SELECT * FROM threads WHERE id = %s", [id])
		# thread = cur.fetchone()
		# m = str(thread['id'])

		cur.execute("UPDATE posts SET post=%s WHERE id = %s", (post, id))

		# commit to DB
		mysql.connection.commit()

		# close connection
		cur.close()

		flash('Post Updated', 'success')

		return redirect(url_for('thread', id=session['thread']))
	return render_template('edit_post.html', form=form)


# Delete POST
@app.route('/delete_post/<string:id>', methods=['GET', 'POST'])
@if_logged_in
def delete_post(id):
	# create cursor
	cur = mysql.connection.cursor()

	# execute


	cur.execute("DELETE FROM posts WHERE id = %s", [id])

	# commit to DB
	mysql.connection.commit()

	# close connection
	cur.close()

	flash('Post Deleted', 'success')

	return redirect(url_for('thread', id=session['thread']))



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
