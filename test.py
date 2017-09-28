
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello Napier"

@app.route('/static-example/img')
def static_example_img():
  start = '<img src="'
  url = url_for('static', filename='vmask.jpg')
  end = '">'
  return start+url+end, 200

@app.route('/force404')
def force404():
  abort(404)

@app.errorhandler(404)
def page_not_found(error):
  return "couldn't not find the page requested.", 404

@app.route("/private")
def private():
# test for user logged in failed
# so redirect to login URL
  return redirect(url_for('login'))

@app.route('/login')
def login():
  return "now we would get pass and username"

@app.route("/account/", methods=['GET', 'POST'])
def account():
  if request.method == 'POST':
    return "POST'ed to /account root\n"
  else:
    return "GET /account root"

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)


