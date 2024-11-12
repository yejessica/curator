from flask import Blueprint, jsonify, render_template, g
from sqlalchemy import *

users_bp = Blueprint('users', __name__)

#Get all exhibits owned by a user
@users_bp.route('/users/allCollections/<int:user_id>', methods=['GET'])
def get_user_collections(user_id):
    result = g.conn.execute(text("""
        SELECT * FROM Collections 
        WHERE user_id = :user_id
    """), {"user_id": user_id})
    collections = [row._asdict() for row in result]
    # Use the below line if we're using only the backend!
    return render_template('renderCollections.html', collections=collections)
    # return jsonify(collections=collections)