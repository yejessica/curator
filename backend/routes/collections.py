from flask import Blueprint, jsonify, render_template, g, request
from sqlalchemy import *

collections_bp = Blueprint('collections', __name__)

@collections_bp.route('/collections/showAll', methods=['GET'])
def get_all_collections():
    # engine = current_app.config['DB_ENGINE']

    with g.conn as conn:
        result = conn.execute(text("SELECT * FROM collections"))
        collections = [row._asdict() for row in result]

    # return jsonify({"message": f"User: {user_id}", "collections": collections})
    return render_template("renderCollections.html", collections = collections)


# Gets all the exhibits from a Collection
@collections_bp.route('/collections/getExhibits/<int:collection_id>', methods=['GET'])
def get_collection_exhibits(collection_id):
    result = g.conn.execute(text("""
        SELECT * FROM Exhibits
        WHERE collection_id = :collection_id
    """), {"collection_id": collection_id})
    exhibits = [row._asdict() for row in result]
    return render_template('renderCollections.html', collections=exhibits)

# need to test, add an exhibit to collection.
@collections_bp.route('/collections/addExhibit')
def add_exhibit():
    data = request.get_json()

    insertSQL = """
        INSERT INTO exhibits (title, height, width, xcoord, ycoord, exhibit_format, collection_id, user_id)
        VALUES (%s, %i, %i, %i, %i, %s, %i, %i)
    """
    try: 
        g.conn.execute(sql, (data['title'],data['height'],data['width'],data['xcoord'],data['ycoord'],data['exhibit_format'],data['collection_id'],data['user_id']))

        return jsonify({'message': 'Exhibit added successfully'}), 201
    except Exception as e:
        g.conn.rollback()
        return jsonify({'message': 'Error adding exhibit', 'error': str(e)}), 400
    
# adding a collection
@collections_bp.route('/collections/addCollection')
def add_collection():
    data = request.get_json()

    insertSQL = """
        INSERT INTO collections (url, title, user_id)
        VALUES (%s, %s, %i)
    """
    try: 
        g.conn.execute(sql, (data['url'],data['title'],data['user_id']))

        return jsonify({'message': 'Collection added successfully'}), 201
    except Exception as e:
        g.conn.rollback()
        return jsonify({'message': 'Error adding collection', 'error': str(e)}), 400
