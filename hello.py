from flask import Flask, redirect, url_for, abort
app = Flask(__name__)

@app.route("/")
def root():
  return "the default, 'root' route"

@app.route("/hello/")
def hello():
    return "hello Napier!! :d"

@app.route("/goodbye/")
def goodbye():
  return "Goodbye cruel world :("

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
