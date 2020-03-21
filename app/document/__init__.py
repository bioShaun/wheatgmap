from flask import Blueprint

document = Blueprint('document', __name__, url_prefix='/document')

from . import views
