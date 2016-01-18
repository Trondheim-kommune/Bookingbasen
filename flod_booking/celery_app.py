from __future__ import absolute_import
import os
from logging import StreamHandler
from celery import Celery, task, current_task
import emails
from flask import Flask
from database import init_db

def create_celery_app(flask_app=None):    
    # Here we are instantiating a Celery object and handing it a 
    # list containing the relative (to where you start your Celery daemon) 
    # path to all modules containing Celery tasks.
    celery_app = Celery('app', include=['celery_tasks.email_tasks','celery_tasks.notifications_strotimer'])    

    # Import Celery config file
    celery_app.config_from_object('celeryconfig')    
    celery_app.conf.update(flask_app.config)

    # This custom class creates an application context before any task is run. 
    # This is necessary because task methods will most likely be using code that 
    # is shared by the web application. More specifically, a task might query or 
    # modify the database via the Flask-SQLAlchemy extension which requires an 
    # application context to be present when interacting with the database.
    TaskBase = celery_app.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with flask_app.app_context() and flask_app.test_request_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery_app.Task = ContextTask    
    return celery_app

def create_flask_app(db_url):
    app = Flask(__name__)
    (app.db_session, app.db_metadata, app.db_engine) = init_db(db_url)
    app.debug = os.environ.get('DEBUG') == 'True'
    app.testing = os.environ.get('TESTING') == 'True'
    @app.teardown_request
    def shutdown_session(exception=None):
        app.db_session.remove()
    return app

flask_app = create_flask_app(os.environ.get('BOOKING_DATABASE_URL', 'sqlite:////tmp/flod_booking.db'))   
if not flask_app.debug:
    stream_handler = StreamHandler()
    flask_app.logger.addHandler(stream_handler)
emails.init_email(flask_app)
celery_app = create_celery_app(flask_app)    

if __name__ == '__main__':    
    celery_app.start()
