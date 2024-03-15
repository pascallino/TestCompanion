import os

base_url = os.path.dirname(os.path.abspath(__name__))
class Config:
    DEBUG = True
    JWT_SECRET_KEY = 'X-ACCESS-LOGIN-FOUNDATIONS-PROJECT'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "7JNJHGHjhhjjFF"
    UPLOAD_FOLDER = base_url
    password = 'TestCompanion'
    db = f'mysql+pymysql://TestCompanion:{password}@localhost:3306/TestCompanion'
    SQLALCHEMY_DATABASE_URI = db
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_url, 'Database.db')

