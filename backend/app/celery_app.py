"""Celery application factory for docker-compose worker startup."""
import os

from celery import Celery

from app import create_app


def _make_celery():
    flask_app = create_app(os.environ.get('FLASK_ENV', 'production'))
    broker_url = flask_app.config.get('REDIS_URL', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

    celery = Celery(
        flask_app.import_name,
        broker=broker_url,
        backend=broker_url
    )
    celery.conf.update(
        broker_connection_retry_on_startup=True,
        task_ignore_result=True
    )

    class FlaskContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskContextTask
    return celery


celery = _make_celery()
