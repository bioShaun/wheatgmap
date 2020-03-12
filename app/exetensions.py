from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_login import LoginManager

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

mail = Mail()
db = SQLAlchemy(use_native_unicode='utf8mb4',
                metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
login_manager = LoginManager()
