import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"

def schedule_job():
    print("Scheduled job running.")
    # A scheduled job to load tickets and process matches 

sched = BackgroundScheduler(daemon=True)
sched.add_job(schedule_job,'interval',minutes=1)
sched.start()

atexit.register(lambda: sched.shutdown())

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @app.before_first_request
    def init_data():
        s = db.session()

        from .models import User
        user = User.query.first()
        if user == None:
            new_user = User(email="chris@aldred.cloud", password=generate_password_hash("admin123", method='sha256'), first_name="Chris", last_name="Aldred")
            s.add(new_user)
            s.commit()
        
        user = User.query.first()
        from .models import Article
        article = Article.query.first()
        if article == None:
            new_article = Article("_init_article", "TEST BODY", user.id)
            s.add(new_article)
            s.commit()

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')