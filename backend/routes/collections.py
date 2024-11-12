from flask import Blueprint, jsonify, current_app, render_template, g
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


#Get all exhibits owned by a user
@collections_bp.route('/collections/<int:user_id>', methods=['GET'])
def get_user_collections(user_id):
    result = g.conn.execute(text("""
        SELECT * FROM Collections 
        WHERE user_id = :user_id
    """), {"user_id": user_id})
    collections = [row._asdict() for row in result]
    return render_template('renderCollections.html', collections=collections)

# Gets all the exhibits from a Collection
@collections_bp.route('/collections/getExhibits/<int:collection_id>', methods=['GET'])
def get_collection_exhibits(collection_id):
    result = g.conn.execute(text("""
        SELECT * FROM Exhibits
        WHERE collection_id = :collection_id
    """), {"collection_id": collection_id})
    exhibits = [row._asdict() for row in result]
    return render_template('renderCollections.html', collections=exhibits)