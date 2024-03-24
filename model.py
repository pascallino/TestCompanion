from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from uuid  import uuid4
from datetime import datetime
from flask_login import  UserMixin
import hashlib

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)



class Emailserver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emailid = db.Column(db.String(128), nullable=False, unique=True)
    sender =  db.Column(db.String(255), nullable=False)
    cc =  db.Column(db.String(255), nullable=True)
    mail_server =  db.Column(db.String(255), nullable=False)
    mail_port = db.Column(db.Integer, nullable=False)
    mail_use_tls = db.Column(db.Boolean, default=True)
    mail_use_ssl = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.String(255), default='No')
    
    def __init__(self, *args, **kwargs):
        self.emailid = str(uuid4())
        super().__init__(*args, **kwargs)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255), nullable=False)
    test_id = db.Column(db.String(128), nullable=False, unique=True)
    created = db.Column(db.DateTime, default=datetime.now())
    userid = db.Column(db.String(128), db.ForeignKey('user.userid'), nullable=False)
    questions = db.relationship('Question', backref='test', lazy=True)
    teststats = db.relationship('Teststat', backref='test', lazy=True)
    
    def __init__(self, test_name):
        self.test_name = test_name
        self.test_id = str(uuid4())

class Teststat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.String(128), db.ForeignKey('test.test_id'), nullable=False)
    test_day_id = db.Column(db.String(128), nullable=False, unique=True)
    test_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=0)
    status =  db.Column(db.String(128), nullable=False, default='pending')
    applicanttests = db.relationship('Applicanttest', backref='teststat', lazy=True)
  
    def __init__(self, test_date, duration):
        self.test_day_id = str(uuid4())
        self.test_date = test_date
        self.duration = duration
    
class Applicanttest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(128), nullable=False)
    #test_date = db.Column(db.DateTime, nullable=False)
    test_day_id = db.Column(db.String(128), db.ForeignKey('teststat.test_day_id'), nullable=False)
    secret_key = db.Column(db.String(128), nullable=False)
    started = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, nullable=True)
    #test_day_id = db.Column(db.String(128), nullable=False)
    #duration = db.Column(db.Integer, default=0)  # New field
    test_status = db.Column(db.String(128), nullable=False, default='pending')
    score = db.Column(db.Integer, default=0) 

    def __init__(self, user_email, start_date, fullname):
        self.start_date = start_date
        #self.test_day_id = test_day_id
        self.user_email = user_email
        self.fullname = fullname
        self.user_id =  str(uuid4())[-9:]
        #self.test_id = test_id
        self.secret_key =  str(uuid4())[-9:]
    

class Userquestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.String(255), nullable=False)
    Qnum = db.Column(db.Integer, nullable=True)
    answer_chosen = db.Column(db.String(255))
    created_date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, user_id, question_id, answer_chosen=None, Qnum=None):
        self.user_id = user_id
        self.question_id = question_id
        self.answer_chosen = answer_chosen
        self.Qnum = Qnum

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.String(128), nullable=False, unique=True)
    Qnum = db.Column(db.Integer, nullable=True)
    correct_answer = db.Column(db.String(128), nullable=True)
    test_id = db.Column(db.String(128), db.ForeignKey('test.test_id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    options = db.relationship('Option', backref='question', lazy=True)

    def __init__(self, text, question_id=None, *args, **kwargs):
        super().__init__(text=text, question_id=question_id, *args, **kwargs)
        if not question_id:
            self.question_id = str(uuid4()).replace("-", "")

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    Opnum = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.String(128), db.ForeignKey('question.question_id'), nullable=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    companyid = db.Column(db.String(255), unique=True, nullable=True)
    company_name = db.Column(db.String(255), nullable=False)
    company_email = db.Column(db.String(255), nullable=False)
    company_website = db.Column(db.String(255), nullable=True)
    company_address = db.Column(db.Text, nullable=False)
    confirm = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='company', lazy=True)
    
    def __init__(self, company_name, company_email, company_website,company_address):
        self.companyid = str(uuid4())
        self.company_name = company_name
        self.company_email = company_email
        self.company_address = company_address
        self.company_website = company_website
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(128), unique=True, nullable=True)
    company_id = db.Column(db.String(255), db.ForeignKey('company.companyid'), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    _password = db.Column('password',
                        db.String(128),
                        nullable=False)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    role = db.Column(db.String(10), nullable=True)
    created = db.Column(db.DateTime, default=datetime.now())
    tests = db.relationship('Test', backref='user', lazy=True)
   
    def __init__(self, *args, **kwargs):
        """initializes user"""
        self.userid = str(uuid4())
        super().__init__(*args, **kwargs)

    # def __repr__(self):
    # return f"<User id: {self.id} Names: {self.first_name} {self.last_name}>"
    
    def is_authenticated(self):
        return True  # Assuming all users are authenticated

    def is_active(self):
        return True  # Assuming all users are active

    def is_anonymous(self):
        return False  # False for regular users, True for an anonymous user

    def get_id(self):
        return str(self.id)
    
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, pwd):
        """hashing password values"""
        self._password = hashlib.md5(pwd.encode()).hexdigest()
