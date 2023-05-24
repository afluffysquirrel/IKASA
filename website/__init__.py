from flask_apscheduler import APScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from website.utils.init_data import init_data
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
        from .auth import auth
        from .logic.root import rootBluePrint
        from .logic.home import homeBluePrint
        from .logic.articles import articlesBluePrint
        from .logic.tickets import ticketsBluePrint
        from .logic.admin import adminBluePrint
        from .logic.account import accountBluePrint
        from .logic.tasks import tasksBluePrint
        from .logic.uploads import uploadsBluePrint

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(rootBluePrint, url_prefix='/')
    app.register_blueprint(homeBluePrint, url_prefix='/home')
    app.register_blueprint(articlesBluePrint, url_prefix='/articles')
    app.register_blueprint(ticketsBluePrint, url_prefix='/tickets')
    app.register_blueprint(adminBluePrint, url_prefix='/admin')
    app.register_blueprint(accountBluePrint, url_prefix='/user')
    app.register_blueprint(tasksBluePrint, url_prefix='/tasks')
    app.register_blueprint(uploadsBluePrint, url_prefix='/uploads')

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
