from flask import Flask
from flask import flash, redirect, render_template, request, session, abort, jsonify, g, redirect, Response
import os
from routes import blueprints
from sqlalchemy import *
from sqlalchemy.pool import NullPool



app = Flask(__name__)
DB_USER = "jj3390"
DB_PASSWORD = "quesadillas"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


app.config['DB_ENGINE'] = create_engine(DATABASEURI)

engine = create_engine(DATABASEURI)
for bp in blueprints:
   app.register_blueprint(bp)


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
    # This renders an HTML file that loads the Next.js app.
    return render_template('index.html')

# @app.route('/api/data')
# def get_data():
#     return {"message": "Hello from Flask!"}


# def home():
#    if not session.get('logged_in'):
#       return render_template('login.html')
#    else:
#       return "Hello Boss!"

# @app.route('/login', methods=['POST'])
# def do_admin_login():
#    if request.form['password'] == 'password' and request.form['username'] == 'admin':
#       session['logged_in'] = True
#    else:
#       flash('wrong password!')
#    return home()


if __name__ == "__main__":
   app.secret_key = os.urandom(12)
   app.run(debug=True,host='0.0.0.0', port=4000)