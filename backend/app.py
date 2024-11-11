from flask import Flask
from flask import flash, redirect, render_template, request, session, abort
import os
from routes import blueprints

app = Flask(__name__)

for bp in blueprints:
    app.register_blueprint(bp)

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