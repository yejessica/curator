import os
from flask import Flask, request, jsonify, session, g
from sqlalchemy import create_engine, text
import bcrypt
from flask_cors import CORS
import secrets
import uuid

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Use the provided secret key
# app.secret_key = secrets.token_hex(32).encode('utf-8')

app.secret_key = b'4b629ea0a2f866fd344b0c8b2371c538d9ffab2283595e05d3cece580328fe1b'

DB_USER = "jj3390"
DB_PASSWORD = "quesadillas"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/w4111"

app.config['DB_ENGINE'] = create_engine(DATABASEURI)
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
        # Print the logged-in user's email from the session, if it exists
        if 'email' in session:
            print(f"Logged in as: {session['email']}")
        else:
            print("No user is currently logged in.")
    except:
        print("Uh oh, problem connecting to the database")
        import traceback
        traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

# Endpoint for user registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"error": "All fields are required."}), 400

    try:
        # Check if the user already exists
        existing_user = g.conn.execute(
            text("SELECT * FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing_user:
            return jsonify({"error": "Email is already registered."}), 409

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create the uuid
        random_uuid = uuid.uuid4()
        # Insert the new user into the database
        g.conn.execute(
            text("INSERT INTO Users (user_id, username, email, password) VALUES (:user_id, :username, :email, :password)"),
            {"user_id": random_uuid, "username": username, "email": email, "password": hashed_password}
        )
        g.conn.commit()

        print(f"User {email} successfully registered.")
        return jsonify({"message": "Registration successful!"}), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": "An error occurred during registration."}), 500



# Endpoint for login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        user = g.conn.execute(
            text("SELECT * FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if user is None:
            return jsonify({"error": "Email not found."}), 404

        db_password = user[3]  # Assuming the password is the 4th column
        username = user[1]
        # print(username)
        if not bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
            return jsonify({"error": "Incorrect password."}), 401

        # Store the user's email in the session
        session['email'] = email
        session['username'] = username
        print(f"User {email} successfully logged in.")

        return jsonify({"message": "Login successful!"}), 200
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({"error": "An error occurred during login."}), 500

# Endpoint for logout
@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    if 'email' in session:
        print(f"Logging out user: {session['email']}")
        session.pop('email', None)
    else:
        print("No user was logged in to log out.")
    return jsonify({"message": "Logout successful!"}), 200

# New endpoint 1: Check user profile
@app.route('/api/profile', methods=['GET'])
def profile():
    if 'email' in session:
        return jsonify({"message": f"User profile for {session['email']}"}), 200
    else:
        return jsonify({"error": "User not logged in."}), 401

# New endpoint 2: Access secure data
@app.route('/api/secure-data', methods=['GET'])
def secure_data():
    if 'email' in session:
        return jsonify({"message": f"Here is some secure data for {session['email']}"}), 200
    else:
        return jsonify({"error": "User not logged in."}), 401
    
@app.route('/api/current-email', methods=['GET'])
def get_current_email():
    email = session.get('email')  # Retrieve the email from the session
    if email:
        # collections = g.conn.execute(SELECT * FROM collections WHERE user = )
        return jsonify({"email": email}), 200
    return jsonify({"error": "No email found in session"}), 404

@app.route('/api/all-user-collections', methods= ['GET'])
def get_all_user_collections():
    email = session.get('email')
    username = session.get('username')
    if email:
        result = g.conn.execute(
            text("""
            SELECT c.collection_id, c.url, c.title, c.views, c.likes, c.user_id
            FROM Collections c
            JOIN Users u ON c.user_id = u.user_id
            WHERE u.email = :email;
            """),
            {"email":email}
        )

        collections = []
        for row in result:
            collections.append({
                'collection_id': row[0],  # Accessing by index
                'url': row[1],
                'title': row[2],
                'views': row[3],
                'likes': row[4],
                'user_id': row[5]
        })
            


        # collections = [dict(row) for row in result]
        return jsonify({"email": email, "username": username, "collections":collections}), 200
    
    return jsonify({"error": "No email found in session"}), 404

# Route to get exhibits by collection_id
@app.route('/api/collection/<uuid>', methods=['GET'])
def get_collection_data(uuid):
    if g.conn:
        try:
            # Query to get exhibits and relevant data
            query = text("""
                SELECT exhibits.title, exhibits.created_at, exhibits.exhibit_format, exhibits.xcoord, exhibits.ycoord,
                       exhibits.height, exhibits.width, users.username
                FROM exhibits
                JOIN collections ON exhibits.collection_id = collections.collection_id
                JOIN users ON collections.user_id = users.user_id
                WHERE collections.collection_id = :uuid
            """)
            # Pass the parameter as a dictionary
            result = g.conn.execute(query, {"uuid": uuid})
            exhibits = [dict(row) for row in result]
            print(exhibits)
            return jsonify({"exhibits": exhibits}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)