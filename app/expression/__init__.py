from flask import Blueprint

expression = Blueprint('expression', __name__, url_prefix='/expression')

from . import views
