from flask import Blueprint

mapping = Blueprint('mapping', __name__, url_prefix='/mapping')

from . import views
