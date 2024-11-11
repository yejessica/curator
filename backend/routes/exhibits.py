from flask import Blueprint, jsonify, current_app, render_template, g
from sqlalchemy import *

exhibits_bp = Blueprint('exhibits', __name__)



@exhibits_bp.route('/exhibits')
def exhibit_index():
    try:
        # This renders an HTML file that loads the Next.js app.
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering template: {str(e)}")
        return str(e), 500
# Add exhibit to collection