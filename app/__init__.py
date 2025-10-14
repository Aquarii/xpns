from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from config import config
from flask_login import LoginManager


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    return app 

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

app = create_app()
app.config.from_object(config['default'])

class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(naming_convention=convention)
    pass


# Extensions initialization
db = SQLAlchemy(app, model_class=Base, engine_options={"echo": True, "echo_pool": False})
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'دسترسی به این صفحه فقط برای مدیر امکان پذیر است. اگر مدیر هستید وارد شوید...'
login.login_message_category = 'warning'

from app import routes, models
