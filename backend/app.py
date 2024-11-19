import os
from flask import Flask, request, jsonify, session, g
from sqlalchemy import create_engine, text
import bcrypt
from flask_cors import CORS
import secrets
import uuid
import random
import string

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Use the provided secret key
app.secret_key = secrets.token_hex(32).encode('utf-8')
# app.secret_key = b'4b629ea0a2f866fd344b0c8b2371c538d9ffab2283595e05d3cece580328fe1b'

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
        g.conn.commit()
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
        # return jsonify({"message": f"User profile for {session['email']}"}), 200
        return jsonify({"email": session['email'], "username": session['username']})
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
@app.route('/api/collection/<url>', methods=['GET'])
def get_collection_data(url):
    if not g.conn:
        print("Debug: Failed to connect to the database.")
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        print(f"Debug: Starting to fetch exhibits for collection ID: {url}")
        # Pre-processing step: Figure out what the uuid is (url --> uuid)
        query = text("""
            SELECT collections.collection_id FROM collections WHERE collections.url = :url
        """)
        result = g.conn.execute(query, {"url": url}).fetchone()

        if result is None:
            raise ValueError("No collection found for the given URL.")
        collection_id = result[0]
        # print(collection_id)
                  
        # Get collection-related information
        query = text("""
            SELECT * FROM collections WHERE collections.collection_id = :collection_id
        """)

        result = g.conn.execute(query, {"collection_id": collection_id}).fetchone()
        title = result[2]
        views = result[3]
        likes = result[4]
        user_id = result[5]

        print("Debug: Successfully collected information (title, views, likes, user_id) about collection")

        if result is None:
            raise ValueError("No collection found for the given URL.")
        
        # Get the collection owner's username
        query = text("""
            SELECT * FROM users WHERE users.user_id = :user_id
        """)
        result = g.conn.execute(query, {"user_id": user_id}).fetchone()

        collection_username = result[1]

        if result is None:
            raise ValueError("No username found for the given user_id")

        
        # Step 1: Fetch all exhibits and their tags in one query
        query = text("""
            SELECT exhibits.exhibit_id, exhibits.title, exhibits.created_at, exhibits.exhibit_format,
                   exhibits.xcoord, exhibits.ycoord, exhibits.height, exhibits.width, tags.name AS tag
            FROM exhibits
            LEFT JOIN tags ON exhibits.exhibit_id = tags.exhibit_id
            WHERE exhibits.collection_id = :uuid
        """)
        result = g.conn.execute(query, {"uuid": collection_id})
        print("Debug: Query executed successfully.")

        # Use row._mapping for safer conversion to dictionaries
        exhibits = []
        for row in result:
            try:
                print(f"Debug: Converting row to dictionary: {row}")
                exhibits.append(dict(row._mapping))  # Use row._mapping for conversion
            except AttributeError as e:
                print(f"Debug: Error converting row to dictionary: {e}")
                return jsonify({"error": "Row object does not support '_mapping'. Please check the database driver or SQLAlchemy version."}), 500

        print("Debug: Successfully converted all rows to dictionaries.")

        # Step 2: Organize exhibits and their tags
        exhibit_dict = {}
        for exhibit in exhibits:
            exhibit_id = exhibit["exhibit_id"]
            print(f"Debug: Processing exhibit ID: {exhibit_id}")
            if exhibit_id not in exhibit_dict:
                exhibit_dict[exhibit_id] = {
                    "exhibit_id": exhibit_id,
                    "title": exhibit["title"],
                    "created_at": exhibit["created_at"],
                    "exhibit_format": exhibit["exhibit_format"],
                    "xcoord": exhibit["xcoord"],
                    "ycoord": exhibit["ycoord"],
                    "height": exhibit["height"],
                    "width": exhibit["width"],
                    "tags": set(),
                    "format_specific": {}
                }
            if exhibit["tag"]:
                print(f"Debug: Adding tag '{exhibit['tag']}' to exhibit ID: {exhibit_id}")
                exhibit_dict[exhibit_id]["tags"].add(exhibit["tag"])

        # Convert sets to lists for JSON serialization
        for exhibit in exhibit_dict.values():
            print(f"Debug: Converting tags set to list for exhibit ID: {exhibit['exhibit_id']}")
            exhibit["tags"] = list(exhibit["tags"])

        # Step 3: Fetch format-specific data for each exhibit
        for exhibit in exhibit_dict.values():
            exhibit_id = exhibit["exhibit_id"]
            exhibit_format = exhibit["exhibit_format"]
            print(f"Debug: Fetching format-specific data for exhibit ID: {exhibit_id}, format: {exhibit_format}")

            if exhibit_format == "Images":
                image_query = text("SELECT url FROM images WHERE exhibit_id = :exhibit_id")
                image_result = g.conn.execute(image_query, {"exhibit_id": exhibit_id})
                exhibit["format_specific"]["images"] = [dict(row._mapping) for row in image_result]
                print(f"Debug: Found {len(exhibit['format_specific']['images'])} image(s) for exhibit ID: {exhibit_id}")

            elif exhibit_format == "Videos":
                video_query = text("SELECT url FROM videos WHERE exhibit_id = :exhibit_id")
                video_result = g.conn.execute(video_query, {"exhibit_id": exhibit_id})
                exhibit["format_specific"]["videos"] = [dict(row._mapping) for row in video_result]
                print(f"Debug: Found {len(exhibit['format_specific']['videos'])} video(s) for exhibit ID: {exhibit_id}")

            elif exhibit_format == "Embeds":
                embed_query = text("SELECT url FROM embeds WHERE exhibit_id = :exhibit_id")
                embed_result = g.conn.execute(embed_query, {"exhibit_id": exhibit_id})
                exhibit["format_specific"]["embeds"] = [dict(row._mapping) for row in embed_result]
                print(f"Debug: Found {len(exhibit['format_specific']['embeds'])} embed(s) for exhibit ID: {exhibit_id}")

            elif exhibit_format == "Texts":
                text_query = text("SELECT text, font FROM texts WHERE exhibit_id = :exhibit_id")
                text_result = g.conn.execute(text_query, {"exhibit_id": exhibit_id})
                exhibit["format_specific"]["texts"] = [dict(row._mapping) for row in text_result]
                print(f"Debug: Found {len(exhibit['format_specific']['texts'])} text(s) for exhibit ID: {exhibit_id}")

        print("Debug: Successfully fetched all format-specific data.")
        print(exhibit["format_specific"])
        return jsonify({"exhibits": list(exhibit_dict.values()), "title": title, "views": views, "likes": likes, "collection_username": collection_username}), 200

    except Exception as e:
        print(f"Debug: Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500

    
# Endpoint to get exhibit data including tags and collection name
@app.route('/api/exhibit/<uuid>', methods=['GET'])
def get_exhibit_data(uuid):
    if g.conn:
        try:
            # Query to get the main exhibit data and tags
            main_query = text("""
                SELECT exhibits.title, exhibits.created_at, exhibits.exhibit_format, exhibits.xcoord, exhibits.ycoord,
                       exhibits.height, exhibits.width, collections.title AS collection_name, tags.name AS tag
                FROM exhibits
                JOIN collections ON exhibits.collection_id = collections.collection_id
                LEFT JOIN tags ON exhibits.exhibit_id = tags.exhibit_id
                WHERE exhibits.exhibit_id = :uuid
            """)
            main_result = g.conn.execute(main_query, {"uuid": uuid})
            exhibits = [dict(row) for row in main_result]

            if exhibits:
                # Base exhibit data
                exhibit_data = exhibits[0]
                exhibit_data["tags"] = list({row["tag"] for row in exhibits if row["tag"]})

                # Format-specific data (depending on embed)
                format_specific_data = {}

                if exhibit_data["exhibit_format"] == "Images":
                    image_query = text("SELECT url FROM images WHERE exhibit_id = :uuid")
                    image_result = g.conn.execute(image_query, {"uuid": uuid})
                    format_specific_data["images"] = [dict(row) for row in image_result]

                elif exhibit_data["exhibit_format"] == "Embeds":
                    embed_query = text("SELECT url FROM embeds WHERE exhibit_id = :uuid")
                    embed_result = g.conn.execute(embed_query, {"uuid": uuid})
                    format_specific_data["embeds"] = [dict(row) for row in embed_result]

                elif exhibit_data["exhibit_format"] == "Texts":
                    text_query = text("SELECT text, font FROM texts WHERE exhibit_id = :uuid")
                    text_result = g.conn.execute(text_query, {"uuid": uuid})
                    format_specific_data["texts"] = [dict(row) for row in text_result]

                elif exhibit_data["exhibit_format"] == "Videos":
                    video_query = text("SELECT url FROM videos WHERE exhibit_id = :uuid")
                    video_result = g.conn.execute(video_query, {"uuid": uuid})
                    format_specific_data["videos"] = [dict(row) for row in video_result]

                exhibit_data["format_specific"] = format_specific_data
            else:
                exhibit_data = None

            return jsonify({"exhibit": exhibit_data}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    # Check if the user is logged in by checking the session
    if 'email' in session and 'username' in session:
        return jsonify({"authenticated": True}), 200
    return jsonify({"authenticated": False}), 401
    
@app.route('/api/create-collection', methods=['POST'])
def create_collection():
    if 'email' not in session:
        return jsonify({"error": "User is not logged in"}), 401

    # Retrieve email from the session
    email = session['email']

    try:
        # Query the database to get the user_id based on the email
        user_query = text("SELECT user_id FROM users WHERE email = :email")
        result = g.conn.execute(user_query, {"email": email})
        user = result.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user[0]  # Retrieve the user_id from the query result

        # Get the data from the request
        data = request.get_json()
        collection_name = data.get('name')
        exhibits = data.get('exhibits', [])

        if not collection_name or not exhibits:
            return jsonify({"error": "Collection name and exhibits are required"}), 400

        # Generate a UUID for the new collection
        collection_uuid = str(uuid.uuid4())

        letters = string.ascii_letters  # Includes both uppercase and lowercase
        url = ''.join(random.choices(letters, k=10))


        # Insert the collection into the database
        insert_collection_query = text("""
            INSERT INTO collections (collection_id, title, url, user_id)
            VALUES (:uuid, :title, :url, :user_id)
        """)
        g.conn.execute(insert_collection_query, {
            "uuid": collection_uuid,
            "title": collection_name,
            "url": url,  # Use the collection_uuid as the url temporarily - CHANGED
            "user_id": user_id
        })

        # Insert each exhibit into the database
        for exhibit in exhibits:
            exhibit_uuid = str(uuid.uuid4())
            exhibit_format = exhibit.get('exhibit_format', '')

            # Insert into the exhibits table
            insert_exhibit_query = text("""
                INSERT INTO exhibits (exhibit_id, collection_id, title, exhibit_format, xcoord, ycoord, height, width, user_id)
                VALUES (:exhibit_id, :collection_id, :title, :exhibit_format, 0, 0, 100, 100, :user_id)
            """)
            g.conn.execute(insert_exhibit_query, {
                "exhibit_id": exhibit_uuid,
                "collection_id": collection_uuid,
                "title": exhibit.get('title', ''),
                "exhibit_format": exhibit_format,
                "user_id": user_id
            })

            # Insert format-specific data based on the exhibit_format
            if exhibit_format == "Images":
                image_id = str(uuid.uuid4())
                insert_image_query = text("INSERT INTO images (image_id, exhibit_id, url) VALUES (:image_id, :exhibit_id, :url)")
                g.conn.execute(insert_image_query, {
                    "image_id": image_id,
                    "exhibit_id": exhibit_uuid,
                    "url": exhibit.get('url', '')
                })

            elif exhibit_format == "Videos":
                video_id = str(uuid.uuid4())
                insert_video_query = text("INSERT INTO videos (video_id, exhibit_id, url) VALUES (:video_id, :exhibit_id, :url)")
                g.conn.execute(insert_video_query, {
                    "video_id": video_id,
                    "exhibit_id": exhibit_uuid,
                    "url": exhibit.get('url', '')
                })

            elif exhibit_format == "Embeds":
                embed_id = str(uuid.uuid4())
                insert_embed_query = text("INSERT INTO embeds (embed_id, exhibit_id, url) VALUES (:embed_id, :exhibit_id, :url)")
                g.conn.execute(insert_embed_query, {
                    "embed_id": embed_id,
                    "exhibit_id": exhibit_uuid,
                    "url": exhibit.get('url', '')
                })

            elif exhibit_format == "Texts":
                text_id = str(uuid.uuid4())
                insert_text_query = text("INSERT INTO texts (text_id, exhibit_id, text, font) VALUES (:text_id, :exhibit_id, :text, :font)")
                g.conn.execute(insert_text_query, {
                    "text_id": text_id,
                    "exhibit_id": exhibit_uuid,
                    "text": exhibit.get('text', ''),
                    "font": exhibit.get('font', '')
                })

        return jsonify({"uuid": url}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)