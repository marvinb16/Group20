from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'WE FREAKING LOVE FARMERS MARKETS'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    #email config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
    app.config['MAIL_PORT'] = 587  # SMTP port (587 for TLS, 465 for SSL)
    app.config['MAIL_USERNAME'] = 'marketmapperfeedback@gmail.com'  # Your email
    app.config['MAIL_PASSWORD'] = 'ayow zboo ashy wrks'  # Your email password
    app.config['MAIL_USE_TLS'] = True  # Use TLS
    app.config['MAIL_USE_SSL'] = False  # Not using SSL

    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Post

    with app.app_context():
       db.create_all()

    return app
