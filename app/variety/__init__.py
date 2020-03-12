from flask import Blueprint

variety = Blueprint('variety', __name__, url_prefix='/variety')

from . import views