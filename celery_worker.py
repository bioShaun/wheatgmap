# loading app context to run celery in flask
from app.app import create_app, celery
import time

app = create_app('prod')
app.app_context().push()




