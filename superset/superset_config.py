import os

# Superset specific config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Flask App Builder configuration
# Your App secret key
SECRET_KEY = 'lampung_flood_prediction_2025'

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset_home/superset.db'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Add machine learning prediction endpoints
ENABLE_PROXY_FIX = True

class CeleryConfig(object):
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}

CELERY_CONFIG = CeleryConfig
