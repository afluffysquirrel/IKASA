from flask_apscheduler import APScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .jobs import extract_tickets, calculate_suggestions
import os 
import time
import gc
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}?check_same_thread=False'
    app.config['SCHEDULER_API_ENABLED'] = True
    app.config['SCHEDULER_EXECUTORS'] = {"default": {"type": "threadpool", "max_workers": 2}}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Schedule job config
    def scheduled_job():
        with app.app_context():
            time.sleep(2)
            extract_tickets()
            calculate_suggestions()
        gc.collect()

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    with app.app_context():
        from .views import views
        from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .db_models import User

    create_database(app)
 
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with app.app_context():
        init_data()

    # Starting job schedule
    app.apscheduler.add_job(func=scheduled_job, trigger='date', args=None, id='j1')
    app.apscheduler.add_job(func=scheduled_job, trigger='interval', minutes=5, args=None, id='j2')
    
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

def init_data():
        s = db.session()

        from .db_models import Config
        config = Config.query.first()
        if config == None:
            new_config_1 = Config("rest_api_user", "admin")
            new_config_2 = Config("rest_api_pass", "!s/vm5Zut2PyCXOR")
            new_config_3 = Config("rest_api_ticketing_tool", "ServiceNow")
            new_config_4 = Config("rest_api_url", "https://dev126629.service-now.com")
            new_config_5 = Config("host_url", "")
            s.add(new_config_1)
            s.add(new_config_2)
            s.add(new_config_3)
            s.add(new_config_4)
            s.add(new_config_5)
            s.commit()

        from .db_models import User
        user = User.query.first()
        if user == None:
            new_user = User(
                email="chris@aldred.cloud",
                password="sha256$HYEi1dfUYtJiK5ZU$0bde8f5e9a6ebb98a0a3a3d057ff84a737e2ffe877b4cd753903f7e40bf1dcbc",
                first_name="Chris",
                last_name="Aldred"
            )
            new_user.admin_flag = True
            new_user.approved_flag = True
            s.add(new_user)
            s.commit()

            new_user_2 = User(
                email="admin@email.com",
                password="sha256$fQBYKzsb8r2XZl0h$9f73104475986e7f385c80238ee77f0eb6a950bcfe0111bff405a086aa922d26",
                first_name="test",
                last_name="account"
            )
            new_user_2.admin_flag = True
            new_user_2.approved_flag = True
            s.add(new_user_2)
            s.commit()

        from .db_models import Article
        article = Article.query.first()
        if article == None:
            new_article = Article("How to install and open Adobe Photoshop",
            "Test article",
            "Adobe, Software, Install",
            new_user.id)
            
            s.add(new_article)
            s.commit()

            new_article = Article("How to run Adobe acrobat on PC", "Test article", "Adobe, Acrobat, Software", new_user.id)
            s.add(new_article)
            s.commit()

            new_article = Article("Fix water damaged USB drive", "Test article", "USB, Fix, Water", new_user.id)
            s.add(new_article)
            s.commit()

            new_article = Article("Email server overloaded solution", "Test article", "Email, SFTP, slowness, overloaded", new_user.id)
            s.add(new_article)
            s.commit()

            new_article = Article("Update user password in active directory", "Test article", "Passwords, User, Account, Active Directory", new_user.id)
            s.add(new_article)
            s.commit()