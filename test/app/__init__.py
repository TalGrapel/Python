from fastapi import FastAPI
from mongoengine import connect
from fastapi_mail import ConnectionConfig


SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fast_app = FastAPI()

db_name = 'test'
host = 'localhost'
port = 27017

connect(db = db_name, host=host, port=port)

connection_config = ConnectionConfig(
    MAIL_USERNAME = "donotreplay_yummly@gmail.com",
    MAIL_PASSWORD = "1234",
    MAIL_FROM = "donotreplay_yummly@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = True
)


from app import routes


