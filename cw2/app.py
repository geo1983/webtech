from flask import Flask, render_template
from data import Articles

app = Flask(__name__)

Articles = Articles()

@app.route('/')
def function():
	return render_template('home.html')

@app.route('/threads')
def threads():
	return render_template('threads.html', articles = Articles)

@app.route('/thread/<string:id>/')
def topics(id):
	return render_template('topics.html', id = id)

@app.route('/threads/topic')
def topic():
	return render_template('topic.html')

@app.route('/threads/topic/posts')
def posts():
	return render_template('posts.html')

if __name__ == '__main__':
	app.run(debug=True)
