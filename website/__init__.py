from flask_apscheduler import APScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from .jobs import extract_tickets, calculate_suggestions
import os 
import time
import gc

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
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

        from .models import Config
        config = Config.query.first()
        if config == None:
            new_config_1 = Config("rest_api_user", "admin")
            new_config_2 = Config("rest_api_pass", "O9PvrmPpFoG8")
            new_config_3 = Config("rest_api_ticketing_tool", "ServiceNow")
            new_config_4 = Config("rest_api_url", "https://dev104044.service-now.com")
            s.add(new_config_1)
            s.add(new_config_2)
            s.add(new_config_3)
            s.add(new_config_4)
            s.commit()

        from .models import User
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
                email="jezza@aldred.cloud",
                password="sha256$HYEi1dfUYtJiK5ZU$0bde8f5e9a6ebb98a0a3a3d057ff84a737e2ffe877b4cd753903f7e40bf1dcbc",
                first_name="Jezz",
                last_name="A"
            )
            new_user_2.approved_flag = True
            s.add(new_user_2)
            s.commit()
<<<<<<< HEAD

            new_user_3 = User(
                email="test@test.com",
                password="sha256$GokuWpPgKVDSU1EB$664e23efcf312096190429d98597751326cd6e5605070364f3392014a69518ee",
                first_name="test",
                last_name="account"
            )
            new_user_3.admin_flag = True
            new_user_3.approved_flag = True
            s.add(new_user_3)
            s.commit()
=======
>>>>>>> parent of d833d6c (test admin user)
        
        from .models import Article
        article = Article.query.first()
        if article == None:
            new_article = Article("OBIEE server 403", "Hit the DBA button", "OBIEE, Network, DBA", new_user.id)
            new_article_2 = Article("CMOD529 reached timeout value", "Check BI XMLP server jobs all completed OK", "BI XMLP, Dev", new_user.id)
            new_article_3 = Article("Test user access", "Slow down there nelly", "Accounts, users", new_user_2.id)
            s.add(new_article)
            s.add(new_article_2)
            s.add(new_article_3)
            s.commit()