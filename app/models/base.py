from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
redis = StrictRedis()