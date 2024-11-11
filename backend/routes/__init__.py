# from .users import user_bp
from .collections import collections_bp
from .users import users_bp
from .exhibits import exhibits_bp

# List of all blueprints
blueprints = [collections_bp, exhibits_bp, users_bp]
