from flask import Flask
from celery import Celery
import redis
import os


def make_celery(app:Flask)->Celery:
    # Configure Celery to use Redis as the message broker
    celery = Celery(app.import_name, broker=app.config["CELERY_BROKER_URL"])
    
    # Update Celery config with Flask app's config
    celery.conf.update(result_backend=app.config['CELERY_RESULT_BACKEND'])
    
    # Subclass Task for context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    celery.autodiscover_tasks()
    return celery

def create_redis_client()->redis.Redis:
    redis_client = redis.Redis(host=os.environ.get('REDIS_HOST'),password=os.environ.get('REDIS_PASSWORD','') ,port=6379, db=0)
    return redis_client


