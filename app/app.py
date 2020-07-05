from flask import Flask, render_template
from . import assets
from .exetensions import db, migrate, login_manager, mail, cache
from settings import config, Config

from celery import Celery

celery = Celery(__name__,
                broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_RESULT_BACKEND)


def create_app(config_name):
    app = Flask(__name__)
    celery.conf.update(app.config)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    register_blueprint(app)
    register_exetensions(app)
    register_errorhandlers(app)
    #register_admin(app)
    return app


def register_blueprint(app):
    from app.main import main as main_blueprint
    from app.tools import tools as tools_blueprint
    from app.expression import expression as expression_blueprint
    from app.auth import auth as auth_blueprint
    from app.variants import variants as variants_blueprint
    from app.data import data as data_blueprint
    from app.mapping import mapping as mapping_blueprint
    from app.variety import variety as variety_blueprint
    from app.document import document as document_blueprint
    #from .jbrowse import jbrowse as jbrowse_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(variants_blueprint)
    app.register_blueprint(tools_blueprint)
    app.register_blueprint(expression_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(mapping_blueprint)
    app.register_blueprint(variety_blueprint)
    app.register_blueprint(document_blueprint)
    #app.register_blueprint(jbrowse_blueprint)
    return None


def register_exetensions(app):
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    assets.init_app(app)
    cache.init_app(app)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None

