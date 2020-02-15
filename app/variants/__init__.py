from flask import Blueprint

variants = Blueprint('variants', __name__, url_prefix='/variants')

from . import views
