import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    CONFIG_NAME = "base"
    USE_MOCK_EQUIVALENCY = False
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_NAME = "s2a_cookie"


class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    SECRET_KEY = os.getenv("DEV_SECRET_KEY", "THE_DEV_SECRET_KEY")
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}/app-dev.db".format(basedir)


class TestingConfig(BaseConfig):
    CONFIG_NAME = "test"
    SECRET_KEY = os.getenv("TEST_SECRET_KEY", "THE_TEST_SECRET_KEY")
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}/app-test.db".format(basedir)


class ProductionConfig(BaseConfig):
    CONFIG_NAME = "prod"
    SECRET_KEY = os.getenv("PROD_SECRET_KEY", "THE_PROD_SECRET_KEY")
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}/app-prod.db".format(basedir)


EXPORT_CONFIGS = [
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
]

config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}
