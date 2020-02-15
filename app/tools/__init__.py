from flask import Blueprint

tools = Blueprint('tools', __name__, url_prefix='/tools')

from . import views
