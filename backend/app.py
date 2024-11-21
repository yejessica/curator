import os
from flask import Flask, request, jsonify, session, g
from sqlalchemy import create_engine, text
import hashlib
import base64
from flask_cors import CORS
import secrets
import uuid
import random
import string
import re
import urllib.parse



app = Flask(__name__)
# CORS(app, supports_credentials=True)
CORS(app, supports_credentials=True, origins="*")


# Use the provided secret key
# app.secret_key = secrets.token_hex(32).encode('utf-8')
app.secret_key = b'4b629ea0a2f866fd344b0c8b2371c538d9ffab2283595e05d3cece580328fe1b'

DB_USER = "jj3390"
DB_PASSWORD = "quesadillas"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/w4111"

app.config['DB_ENGINE'] = create_engine(DATABASEURI)
engine = create_engine(DATABASEURI)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)  # Generate a 16-byte salt
    hashed_password = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=16384,  # CPU/memory cost factor
        r=8,      # Block size
        p=1       # Parallelization factor
    )
    # Encode the salt and hashed password in base64 for storage
    return f"{base64.b64encode(salt).decode()}${base64.b64encode(hashed_password).decode()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        # Split the stored hash into salt and hashed password
        salt_b64, hashed_b64 = hashed.split('$')
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(hashed_b64)

        # Hash the provided password with the same salt
        test_hash = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt,
            n=16384,
            r=8,
            p=1
        )

        # Compare the stored hash with the newly computed hash
        return test_hash == stored_hash
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


@app.before_request
def before_request():
    try:
        print("Session before request:", dict(session))
        g.conn = engine.connect()
        # Print the logged-in user's email from the session, if it exists
        if 'email' in session:
            print(f"Logged in as: {session['email']}")
        else:
            print("No user is currently logged in.")
    except:
        print("Session after request:", dict(session))
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
# Cleaning

def clean_username(username):
    if not re.match("^[a-zA-Z0-9_]+$", username):
        raise ValueError("Username contains invalid characters.")
    return username.strip()

def clean_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format.")
    return email.strip()

def clean_password(password):
    if len(password) < 8:  # Adjust password length criteria as needed
        raise ValueError("Password must be at least 8 characters long.")
    return password


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
        clean_email(email)
        cleaned_username = clean_username(username)
        cleaned_password = clean_password(password)


        existing_user = g.conn.execute(
            text("SELECT * FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if existing_user:
            return jsonify({"error": "Email is already registered."}), 409

        # Hash the password
        hashed_password = hash_password(cleaned_password)

        # Create the uuid
        random_uuid = uuid.uuid4()
        # Insert the new user into the database
        g.conn.execute(
            text("INSERT INTO Users (user_id, username, email, password) VALUES (:user_id, :username, :email, :password)"),
            {"user_id": random_uuid, "username": cleaned_username, "email": email, "password": hashed_password}
        )
        g.conn.commit()

        print(f"User {email} successfully registered.")
        return jsonify({"message": "Registration successful!"}), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
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
        clean_email(email)
        clean_password(password)

        user = g.conn.execute(
            text("SELECT * FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()

        if user is None:
            return jsonify({"error": "Email not found."}), 404

        db_password = user[3]  # Assuming the password is the 4th column
        username = user[1]
        # print(username)
        if not verify_password(password, db_password):
            return jsonify({"error": "Incorrect password."}), 401

        # Store the user's email in the session
        session['email'] = email
        session['username'] = username
        print(f"User {email} successfully logged in.")

        return jsonify({"message": "Login successful!"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
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
        # print(exhibit["format_specific"])
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

            print(exhibit_format)

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
                video_url = exhibit.get('url', '')
                def extract_video_id(url):
                    # Check if the URL is from youtu.be or youtube.com
                    if 'youtu.be' in url:
                        # Regular expression to extract video ID from youtu.be URL
                        pattern = r'(?<=youtu\.be/)([^?]+)'
                    elif 'youtube.com' in url:
                        # Regular expression to extract video ID from youtube.com URL
                        pattern = r'(?<=\?v=)([^&]+)'
                    else:
                        return None  # Return None if the URL format is not recognized

                    match = re.search(pattern, url)
                    
                    if match:
                        return match.group(0)
                    else:
                        return None
                
                youtubeUrl = extract_video_id(video_url)
                if (youtubeUrl): #is a youtube url
                    video_url = "https://www.youtube.com/embed/"+youtubeUrl

                print(video_url)
                insert_video_query = text("INSERT INTO videos (video_id, exhibit_id, url) VALUES (:video_id, :exhibit_id, :url)")
                g.conn.execute(insert_video_query, {
                    "video_id": video_id,
                    "exhibit_id": exhibit_uuid,
                    "url": video_url
                })

                


            
            elif exhibit_format == "Embeds":
                embed_id = str(uuid.uuid4())
                embed_url = exhibit.get('url', '')
                # encoded_url = urllib.parse.quote(embed_url)

                
                # print(exhibit.get('url', ''))
                # print(embed_id)
                # try:
                insert_embed_query = text("INSERT INTO embeds (embed_id, url, exhibit_id) VALUES (:embed_id, :url, :exhibit_id)")
                g.conn.execute(insert_embed_query, {
                    "embed_id": embed_id,
                    "exhibit_id": exhibit_uuid,
                    "url": embed_url
                })

                # g.conn.commit()
                print("Record inserted successfully")
            

                # print("hi!!")

                

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

# Endpoint to fetch collection data for editing
@app.route('/api/collection/<url>/edit', methods=['GET'])
def get_collection_for_edit(url):
    if 'email' not in session:
        return jsonify({"error": "User is not logged in"}), 401

    email = session['email']

    try:
        # Get the collection's user_id to verify ownership
        collection_query = text("""
            SELECT c.collection_id, c.title, c.user_id
            FROM Collections c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.url = :url AND u.email = :email
        """)
        result = g.conn.execute(collection_query, {"url": url, "email": email}).fetchone()

        if not result:
            return jsonify({"error": "Collection not found or user is not the owner"}), 403

        collection_id = result[0]
        collection_title = result[1]

        # Fetch all exhibits for the collection
        exhibits_query = text("""
            SELECT e.exhibit_id, e.title, e.exhibit_format, i.url AS image_url, v.url AS video_url, 
                   em.url AS embed_url, t.text, t.font
            FROM Exhibits e
            LEFT JOIN Images i ON e.exhibit_id = i.exhibit_id
            LEFT JOIN Videos v ON e.exhibit_id = v.exhibit_id
            LEFT JOIN Embeds em ON e.exhibit_id = em.exhibit_id
            LEFT JOIN Texts t ON e.exhibit_id = t.exhibit_id
            WHERE e.collection_id = :collection_id
        """)
        exhibits_result = g.conn.execute(exhibits_query, {"collection_id": collection_id}).fetchall()

        exhibits = []
        for row in exhibits_result:
            exhibit = {
                "exhibit_id": row[0],
                "title": row[1],
                "exhibit_format": row[2],
                "url": row[3] or row[4] or row[5] or "",  # Get the appropriate URL
                "text": row[6] or "",
                "font": row[7] or ""
            }
            exhibits.append(exhibit)

        return jsonify({"collection_id": collection_id, "title": collection_title, "exhibits": exhibits}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to update a collection
@app.route('/api/collection/<url>/edit', methods=['POST'])
def update_collection(url):
    if 'email' not in session:
        return jsonify({"error": "User is not logged in"}), 401

    email = session['email']

    try:
        # Verify ownership
        user_query = text("""
            SELECT c.collection_id, c.user_id
            FROM Collections c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.url = :url AND u.email = :email
        """)
        result = g.conn.execute(user_query, {"url": url, "email": email}).fetchone()

        if not result:
            return jsonify({"error": "Collection not found or user is not the owner"}), 403

        collection_id = result[0]

        # Get updated data from the request
        data = request.get_json()
        new_title = data.get('title')
        new_exhibits = data.get('exhibits', [])

        # Update the collection title
        update_title_query = text("""
            UPDATE Collections SET title = :title WHERE collection_id = :collection_id
        """)
        g.conn.execute(update_title_query, {"title": new_title, "collection_id": collection_id})

        # Delete old exhibits
        delete_exhibits_query = text("DELETE FROM Exhibits WHERE collection_id = :collection_id")
        g.conn.execute(delete_exhibits_query, {"collection_id": collection_id})

        # Re-insert updated exhibits
        for exhibit in new_exhibits:
            exhibit_id = exhibit.get("exhibit_id", str(uuid.uuid4()))
            exhibit_format = exhibit.get("exhibit_format", "")
            title = exhibit.get("title", "")

            # Insert into exhibits table
            insert_exhibit_query = text("""
                INSERT INTO Exhibits (exhibit_id, collection_id, title, exhibit_format, xcoord, ycoord, height, width, user_id)
                VALUES (:exhibit_id, :collection_id, :title, :exhibit_format, 0, 0, 100, 100, :user_id)
            """)
            g.conn.execute(insert_exhibit_query, {
                "exhibit_id": exhibit_id,
                "collection_id": collection_id,
                "title": title,
                "exhibit_format": exhibit_format,
                "user_id": result[1]  # Use the user_id from the ownership check
            })

            # Handle format-specific data
            if exhibit_format == "Images":
                image_url = exhibit.get("url", "")
                insert_image_query = text("INSERT INTO Images (image_id, exhibit_id, url) VALUES (:image_id, :exhibit_id, :url)")
                g.conn.execute(insert_image_query, {"image_id": str(uuid.uuid4()), "exhibit_id": exhibit_id, "url": image_url})

            elif exhibit_format == "Videos":
                # video_url = exhibit.get("url", "")
                # insert_video_query = text("INSERT INTO Videos (video_id, exhibit_id, url) VALUES (:video_id, :exhibit_id, :url)")
                # g.conn.execute(insert_video_query, {"video_id": str(uuid.uuid4()), "exhibit_id": exhibit_id, "url": video_url})
                video_url = exhibit.get('url', '')
                def extract_video_id(url):
                    # Check if the URL is from youtu.be or youtube.com
                    if 'youtu.be' in url:
                        # Regular expression to extract video ID from youtu.be URL
                        pattern = r'(?<=youtu\.be/)([^?]+)'
                    elif 'youtube.com' in url:
                        # Regular expression to extract video ID from youtube.com URL
                        pattern = r'(?<=\?v=)([^&]+)'
                    else:
                        return None  # Return None if the URL format is not recognized

                    match = re.search(pattern, url)
                    
                    if match:
                        return match.group(0)
                    else:
                        return None
                
                youtubeUrl = extract_video_id(video_url)
                if (youtubeUrl): #is a youtube url
                    video_url = "https://www.youtube.com/embed/"+youtubeUrl

                print(video_url)
                insert_video_query = text("INSERT INTO videos (video_id, exhibit_id, url) VALUES (:video_id, :exhibit_id, :url)")
                g.conn.execute(insert_video_query, {
                    "video_id": str(uuid.uuid4()),
                    "exhibit_id": exhibit_id,
                    "url": video_url
                })

            elif exhibit_format == "Embeds":
                embed_url = exhibit.get("url", "")
                print("Debug: Embed url "+embed_url)
                insert_embed_query = text("INSERT INTO Embeds (embed_id, exhibit_id, url) VALUES (:embed_id, :exhibit_id, :url)")
                g.conn.execute(insert_embed_query, {"embed_id": str(uuid.uuid4()), "exhibit_id": exhibit_id, "url": embed_url})

            elif exhibit_format == "Texts":
                text_content = exhibit.get("text", "")
                font = exhibit.get("font", "")
                insert_text_query = text("INSERT INTO Texts (text_id, exhibit_id, text, font) VALUES (:text_id, :exhibit_id, :text, :font)")
                g.conn.execute(insert_text_query, {"text_id": str(uuid.uuid4()), "exhibit_id": exhibit_id, "text": text_content, "font": font})

        return jsonify({"message": "Collection updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to increment views for a collection
@app.route('/api/collection/<url>/increment-views', methods=['POST'])
def increment_views(url):
    try:
        # Find the collection by URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        result = g.conn.execute(collection_query, {"url": url}).fetchone()

        if not result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = result[0]

        # Increment the views count
        update_views_query = text("UPDATE Collections SET views = views + 1 WHERE collection_id = :collection_id")
        g.conn.execute(update_views_query, {"collection_id": collection_id})
        g.conn.commit()

        return jsonify({"message": "Views incremented successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to increment likes for a collection
@app.route('/api/collection/<url>/like', methods=['POST'])
def like_collection(url):
    try:
        # Find the collection by URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        result = g.conn.execute(collection_query, {"url": url}).fetchone()

        if not result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = result[0]

        # Increment the likes count
        update_likes_query = text("UPDATE Collections SET likes = likes + 1 WHERE collection_id = :collection_id")
        g.conn.execute(update_likes_query, {"collection_id": collection_id})
        g.conn.commit()

        return jsonify({"message": "Likes incremented successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to save a collection
@app.route('/api/collection/<url>/save', methods=['POST'])
def save_collection(url):
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    email = session['email']

    try:
        # Get user_id from email
        user_query = text("SELECT user_id FROM Users WHERE email = :email")
        user_result = g.conn.execute(user_query, {"email": email}).fetchone()
        if not user_result:
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]

        # Get collection_id from URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        collection_result = g.conn.execute(collection_query, {"url": url}).fetchone()
        if not collection_result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = collection_result[0]

        # Check if the collection is already saved
        check_query = text("SELECT * FROM Saves WHERE user_id = :user_id AND collection_id = :collection_id")
        saved = g.conn.execute(check_query, {"user_id": user_id, "collection_id": collection_id}).fetchone()
        if saved:
            return jsonify({"message": "Collection already saved"}), 200

        # Save the collection
        save_query = text("INSERT INTO Saves (user_id, collection_id) VALUES (:user_id, :collection_id)")
        g.conn.execute(save_query, {"user_id": user_id, "collection_id": collection_id})
        g.conn.commit()

        return jsonify({"message": "Collection saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to check if a collection is saved
@app.route('/api/collection/<url>/is-saved', methods=['GET'])
def is_collection_saved(url):
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    email = session['email']

    try:
        # Get user_id from email
        user_query = text("SELECT user_id FROM Users WHERE email = :email")
        user_result = g.conn.execute(user_query, {"email": email}).fetchone()
        if not user_result:
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]

        # Get collection_id from URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        collection_result = g.conn.execute(collection_query, {"url": url}).fetchone()
        if not collection_result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = collection_result[0]

        # Check if the collection is saved
        check_query = text("SELECT * FROM Saves WHERE user_id = :user_id AND collection_id = :collection_id")
        saved = g.conn.execute(check_query, {"user_id": user_id, "collection_id": collection_id}).fetchone()

        return jsonify({"is_saved": bool(saved)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get saved collections for the user
@app.route('/api/saved-collections', methods=['GET'])
def get_saved_collections():
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    email = session['email']

    try:
        # Get user_id from email
        user_query = text("SELECT user_id FROM Users WHERE email = :email")
        user_result = g.conn.execute(user_query, {"email": email}).fetchone()
        if not user_result:
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]

        # Get saved collections
        saved_collections_query = text("""
            SELECT c.collection_id, c.url, c.title, c.views, c.likes, c.user_id
            FROM Collections c
            JOIN Saves s ON c.collection_id = s.collection_id
            WHERE s.user_id = :user_id
        """)
        saved_collections = g.conn.execute(saved_collections_query, {"user_id": user_id}).fetchall()

        collections = [
            {
                "collection_id": row[0],
                "url": row[1],
                "title": row[2],
                "views": row[3],
                "likes": row[4],
                "user_id": row[5]
            }
            for row in saved_collections
        ]

        return jsonify({"saved_collections": collections}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to unsave a collection
@app.route('/api/collection/<url>/unsave', methods=['POST'])
def unsave_collection(url):
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    email = session['email']

    try:
        # Get user_id from email
        user_query = text("SELECT user_id FROM Users WHERE email = :email")
        user_result = g.conn.execute(user_query, {"email": email}).fetchone()
        if not user_result:
            return jsonify({"error": "User not found"}), 404

        user_id = user_result[0]

        # Get collection_id from URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        collection_result = g.conn.execute(collection_query, {"url": url}).fetchone()
        if not collection_result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = collection_result[0]

        # Remove the saved collection
        delete_query = text("DELETE FROM Saves WHERE user_id = :user_id AND collection_id = :collection_id")
        g.conn.execute(delete_query, {"user_id": user_id, "collection_id": collection_id})
        g.conn.commit()

        return jsonify({"message": "Collection unsaved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint to fetch comments for a collection
@app.route('/api/collection/<url>/comments', methods=['GET'])
def get_comments(url):
    try:
        # Get collection_id from URL
        collection_query = text("SELECT collection_id FROM Collections WHERE url = :url")
        collection_result = g.conn.execute(collection_query, {"url": url}).fetchone()
        if not collection_result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = collection_result[0]

        # Fetch comments
        comments_query = text("""
            SELECT c.comment_id, c.message, c.time, u.username
            FROM Comments c
            JOIN Users u ON c.commenter_user_id = u.user_id
            WHERE c.collection_id = :collection_id
            ORDER BY c.time DESC
        """)
        comments = g.conn.execute(comments_query, {"collection_id": collection_id}).fetchall()

        comments_list = [
            {
                "comment_id": row[0],
                "message": row[1],
                "time": row[2],
                "username": row[3]
            }
            for row in comments
        ]

        return jsonify({"comments": comments_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to add a comment to a collection
@app.route('/api/collection/<url>/comment', methods=['POST'])
def add_comment(url):
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    email = session['email']

    try:
        # Get user_id from email
        user_query = text("SELECT user_id FROM Users WHERE email = :email")
        user_result = g.conn.execute(user_query, {"email": email}).fetchone()
        if not user_result:
            return jsonify({"error": "User not found"}), 404

        commenter_user_id = user_result[0]

        # Get collection_id and owner_id from URL
        collection_query = text("SELECT collection_id, user_id FROM Collections WHERE url = :url")
        collection_result = g.conn.execute(collection_query, {"url": url}).fetchone()
        if not collection_result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = collection_result[0]
        collection_owner_id = collection_result[1]

        # Insert comment
        insert_comment_query = text("""
            INSERT INTO Comments (comment_id, message, time, collection_id, collection_owner_id, commenter_user_id)
            VALUES (:comment_id, :message, NOW(), :collection_id, :collection_owner_id, :commenter_user_id)
        """)
        g.conn.execute(insert_comment_query, {
            "comment_id": str(uuid.uuid4()),
            "message": message,
            "collection_id": collection_id,
            "collection_owner_id": collection_owner_id,
            "commenter_user_id": commenter_user_id
        })
        g.conn.commit()

        return jsonify({"message": "Comment added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to fetch tags for an exhibit
@app.route('/api/exhibit/<exhibit_id>/tags', methods=['GET'])
def get_tags(exhibit_id):
    try:
        # Query to fetch tag names and their counts for the given exhibit_id
        query = text("""
            SELECT name, COUNT(*) as count
            FROM Tags
            WHERE exhibit_id = :exhibit_id
            GROUP BY name
        """)
        result = g.conn.execute(query, {"exhibit_id": exhibit_id})

        # Convert the query results into a list of dictionaries
        tags = [{"name": row[0], "count": row[1]} for row in result]
        return jsonify({"tags": tags}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to add a tag to an exhibit
@app.route('/api/exhibit/<exhibit_id>/tags', methods=['POST'])
def add_exhibit_tag(exhibit_id):
    if 'email' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    tag_name = data.get("tag_name")
    collection_id = data.get("collection_id")  # Get collection_id from the request

    if not tag_name:
        return jsonify({"error": "Tag name is required"}), 400
    if not collection_id:
        return jsonify({"error": "Collection ID is required"}), 400

    try:
        # Get the user ID from the session
        email = session['email']
        user = g.conn.execute(
            text("SELECT user_id FROM Users WHERE email = :email"),
            {"email": email}
        ).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Access the user_id using an integer index
        user_id = user[0]

        # Generate a new UUID for the tag_id
        tag_id = str(uuid.uuid4())

        # Insert the tag into the Tags table
        g.conn.execute(
            text("INSERT INTO Tags (tag_id, name, exhibit_id, collection_id, user_id) VALUES (:tag_id, :name, :exhibit_id, :collection_id, :user_id)"),
            {
                "tag_id": tag_id,
                "name": tag_name,
                "exhibit_id": exhibit_id,
                "collection_id": collection_id,
                "user_id": user_id
            }
        )
        g.conn.commit()  # Commit the transaction
        return jsonify({"message": "Tag added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/collection-id-from-url/<url>', methods=['GET'])
def get_collection_id_from_url(url):
    try:
        # Query the database to get the collection_id using the URL
        query = text("SELECT collection_id FROM Collections WHERE url = :url")
        result = g.conn.execute(query, {"url": url}).fetchone()

        if not result:
            return jsonify({"error": "Collection not found"}), 404

        collection_id = result[0]  # Access collection_id from the result
        return jsonify({"collection_id": collection_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        ssl_context=(
            '/etc/letsencrypt/live/curation.my/fullchain.pem',  # Path to the certificate
            '/etc/letsencrypt/live/curation.my/privkey.pem'     # Path to the private key
        )
    )