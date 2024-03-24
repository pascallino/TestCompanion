from flask import flash, request, render_template, jsonify, url_for, redirect, make_response
import json
from flask_mail import Mail, Message
import MySQLdb
from reportlab.pdfgen import canvas
from sqlalchemy.orm import aliased
import hashlib
from datetime import timedelta
from sqlalchemy import asc, desc, and_, or_, func
from datetime import datetime
from uuid  import uuid4
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_apscheduler import APScheduler
import os

from model import *

#app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
# db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'signin'
login_manager.init_app(app)

scheduler = APScheduler()
scheduler.init_app(app)


#db.init_app(app)

with app.app_context():
    db.create_all()
        
""" @app.before_request
def create_tables():
    db.create_all() """

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
    #return db.session.query(User).get(user_id)

def get_mail_status():
    email = Emailserver.query.all()
    if email:
        return email[0]
    else:
        return ''

@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('About.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('Contact.html')

@app.route('/features', methods=['GET'])
def features():
    return render_template('Features.html')

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('Signup.html')

@app.route('/signin', methods=['GET'])
def signin():
    logout_user()
    return render_template('Signin.html')

@app.route('/sendcontactform', methods=['POST'])
def sendcontactform():
    app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
    app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
    mail = Mail(app)
    json_data = request.json
    body = f"{json_data['message']} \n\nEmail: {json_data['email']}\n\nRegards,\n{json_data['name']} "
    msg = Message('Customer Mail', sender='luvpascal.ojukwu@yahoo.com', recipients=['luvpascal.ojukwu@yahoo.com'],body=body)
    mail.send(msg)
    response_data = {
                'status': 'success',
                'message': 'Thank you for reaching out to us, we have received your message, we will get in touch with you soon'
            }

    return jsonify(response_data), 200

@app.route('/profileboard/<user_id>', methods=['GET'])
@login_required
def profileboard(user_id):
    user = User.query.filter_by(userid=user_id).first()
    if user:
        com = Company.query.filter_by(companyid=user.company_id).first()
        return render_template('profiledashboard.html',
                               companyname=com.company_name,
                               addr=com.company_address,
                               com_email=com.company_email,
                               email=user.email,
                               web=com.company_website,
                               fn=user.first_name,
                               ln=user.last_name,
                               role=user.role,
                               user_id=user_id)

@app.route('/get_profile/<user_id>', methods=['POST'])
@jwt_required()
def get_profile(user_id):
    M = User.query.filter_by(userid=user_id).first()
    json_data = {}
    if M:
        json_data['firstName'] = M.first_name
        json_data['lastName'] =  M.last_name
        json_data['email'] = M.email
        json_data['status'] = 'success'
        json_data['message'] = 'success'
        return  jsonify(json_data), 200
    else:
         json_data['eror'] = 'success'
         json_data['message'] = 'An error Occured, couldnt retrieve your profile'
         return  jsonify(json_data), 500

@app.route('/get_company/<user_id>', methods=['POST'])
@jwt_required()
def get_company(user_id):
    M = User.query.filter_by(userid=user_id).first()
    json_data = {}
    if M:
        com = Company.query.filter_by(companyid=M.company_id).first()
        if com:
            json_data['companyName'] = com.company_name
            json_data['companyWebsite'] = com.company_website
            json_data['companyEmail'] = com.company_email
            json_data['companyAddress'] = com.company_address
            json_data['status'] = 'success'
            json_data['message'] = 'success'
            return  jsonify(json_data), 200
        else:
            json_data['eror'] = 'success'
            json_data['message'] = 'An error Occured, couldnt retrieve company profile'
            return  jsonify(json_data), 500


@app.route('/savecompany/<user_id>', methods=['POST'])
@jwt_required()
def savecompany(user_id):
    try:
        data = request.json
        companyName = data.get('companyName', '')
        companyWebsite = data.get('companyWebsite', '')
        companyEmail = data.get('companyEmail', '')
        companyAddress = data.get('companyAddress', '')
        com = Company.query.filter_by(companyid=current_user.company_id).first()
        if com:
            com.company_name = companyName
            com.company_website = companyWebsite
            com.company_address = companyAddress
            com.company_email = companyEmail
            db.session.commit()
            response_data = {
                'status': 'success',
                'message': 'Company profile updated successfully'
            }
            return jsonify(response_data)
        else:
            response_data = {
                'status': 'error',
                'message': 'Unauthorized access',
                'error': 'Unauthorized access'
            }
            return jsonify(response_data)
    except:
        response_data = {
                'error': 'An error ocured while trying to save the profile',
                'message': 'error'
            }
        return jsonify(response_data)
        
        

@app.route('/saveprofile/<user_id>', methods=['POST'])
@jwt_required()
def saveprofile(user_id):
    try:
        data = request.json
        firstName = data.get('firstName', '')
        lastName = data.get('lastName', '')
        email = data.get('email', '')
        oldpassword = data.get('oldpassword', '')
        newpassword = data.get('newpassword', '')
        
        
        u = User.query.filter_by(userid=user_id).first()
        if u:
            if len(oldpassword.strip()) > 0:
                oldpassword_ = hashlib.md5(oldpassword.encode()).hexdigest()
                if u.password == oldpassword_:
                    u.first_name = firstName
                    u.last_name = lastName
                    u.email = email
                    #u.password = hashlib.md5(newpassword.encode()).hexdigest()
                    u.password = newpassword
                    db.session.commit()
                    response_data = {
                'status': 'success',
                'message': 'Profile data & passoword updated successfully'
            }

                    return jsonify(response_data)
                else:
                    response_data = {
                'error': 'Password is Incorrect',
                'message': 'Password is Incorrect'
            }
                    return  jsonify(response_data)
                    
            else:
                u.first_name = firstName
                u.last_name = lastName
                u.email = email
                db.session.commit()
                response_data = {
                'status': 'success',
                'message': 'Profile data updated successfully'
            }

                return jsonify(response_data)
        else:
            jsonify({'error': 'Unauthorized user'})
    except Exception as e:
      return jsonify({'error': str(e)})
        

@app.route('/testmail/<email_id>/<user_id>', methods=['POST'])
@jwt_required()
def testmail(email_id, user_id):
    try:
        M = Emailserver.query.filter_by(emailid=email_id).first()
        if M:
            app.config['MAIL_SERVER'] = M.mail_server
            app.config['MAIL_PORT'] = M.mail_port
            app.config['MAIL_USE_TLS'] = M.mail_use_tls
            app.config['MAIL_USE_SSL'] = M.mail_use_ssl
            app.config['MAIL_USERNAME'] = M.username
            app.config['MAIL_PASSWORD'] = M.password
            mail = Mail(app)
            user = User.query.filter_by(userid=user_id).first()
            if user:
                body = f"Hi {user.last_name},\n\nThis is to inform you that your mail setting was accepted. \n\nRegards,\n\nTestCompanion team. "
                msg = Message('MAIL TESTING SUCCESSFUL', sender=M.sender, recipients=[M.cc, M.sender],body=body)
                mail.send(msg)
                return jsonify({'message': 'Mail sent successfully', 'status': 'success'})
            else:
                return jsonify({'message': 'Unauthorized user'})
        else:
            return jsonify({'message': 'wrong mail user'})
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'An error occured, please check your mail settings ', 'status': 'error'})

        

@app.route('/updatemailstatus', methods=['POST'])
@jwt_required()
def updatemailstatus():
    direction = request.json
    if direction['direction'] == 'onchange':
        M = Emailserver.query.all()
        if M:
            checked = False
            if M[0].active == 'No':
                M[0].active = 'Yes'
            else:
                M[0].active = 'No'
                checked = True
            db.session.commit()
            return jsonify({'status': 'success', 'message':'Mail settings updated', 'checked': checked})
        else:
            return jsonify({'status': 'error', 'error':'No record found'})
    else:
        M = Emailserver.query.all()
        if M:
            if M[0].active == 'Yes':
                return jsonify({'status': 'success', 'checked': False})
            else:
                return jsonify({'status': 'success', 'checked': True})
        else:
            return jsonify({'status': 'error'})


@app.route('/deletemail/<email_id>', methods=['POST'])
@jwt_required()
def deletemail(email_id):
    data = request.get_json()
    if data:
        M = Emailserver.query.filter_by(emailid=email_id).first()
        if M:
            db.session.delete(M)
            db.session.commit()
            return jsonify({'message': 'All records deleted', 'status': 'success'})
    return jsonify({'message': 'An error occured while performing this operation','status': 'error, not a valid test'})
    
     

@app.route('/get_mail/<email_id>', methods=['POST'])
@jwt_required()
def get_mail(email_id):
    M = Emailserver.query.filter_by(emailid=email_id).first()
    json_data = {}
    if M:
        json_data['sender'] = M.sender
        json_data['cc'] =  M.cc
        json_data['server'] = M.mail_server
        json_data['port'] = M.mail_port
        json_data['TLS'] = M.mail_use_tls
        json_data['SSL'] = M.mail_use_ssl
        json_data['SSL'] = M.mail_use_ssl
        json_data['username'] = M.username
        json_data['password'] = M.password
        json_data['status'] = 'success'
        json_data['message'] = 'success'
        return  jsonify(json_data), 200
    else:
         json_data['eror'] = 'success'
         json_data['message'] = 'An error Occured, couldnt retrieve user data'
         return  jsonify(json_data), 500

@app.route('/get_user/<user_id>', methods=['POST'])
@jwt_required()
def get_user(user_id):
    user = User.query.filter_by(userid=user_id).first()
    json_data = {}
    if user:
        json_data['firstName'] = user.first_name
        json_data['lastName'] =  user.last_name
        json_data['email'] = user.email
        json_data['status'] = 'success'
        json_data['message'] = 'success'
        json_data['role'] = user.role
        return  jsonify(json_data), 200
    else:
         json_data['eror'] = 'success'
         json_data['message'] = 'An error Occured, couldnt retrieve user data'
         return  jsonify(json_data), 500
 
@app.route('/deleteuser/<user_id>', methods=['POST'])
@jwt_required()
def deleteuser(user_id):
    data = request.get_json()
    user = User.query.filter_by(userid=user_id).first()
    if not user:
         return jsonify({'message': 'The user doesn''t exist', 'status': 'error'}), 401  
    tests = Test.query.filter_by(userid=user_id).all()
    for test in tests:
        test_id = test.test_id
        if test:
            Q = Question.query.filter_by(test_id=test_id).all()
            if Q:
                for q in Q:
                    uq = Userquestion.query.filter_by(question_id=q.question_id).all()
                    if uq:
                        for uu in uq:
                            db.session.delete(uu)
                        db.session.commit()  
                    for o in q.options:
                        db.session.delete(o)
                    db.session.delete(q)
                    db.session.commit()

            teststat = Teststat.query.filter_by(test_id=test_id).all()
            if teststat:
                for t in teststat:
                    for app in t.applicanttests:
                        db.session.delete(app)
                    db.session.delete(t)
                    db.session.commit()
            db.session.delete(test)
            db.session.commit()
            # t = Test.query.filter_by(userid=user_id).all()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'All records deleted', 'status': 'success'})
    return jsonify({'message': 'An error occured while performing this operation','status': 'error, not a valid test'})
    
     
     
@app.route('/saveuser/<user_id>', methods=['POST'])
@jwt_required()
def saveuser(user_id):
    try:
        data = request.json
        fn = data.get('firstName', '')
        ln = data.get('lastName', '')
        pwd = data.get('password', '')
        email = data.get('email', '')
        mod = data.get('mod', '')
        role = data.get('role', '')
        moduserid = data.get('moduserid', '')

        user = User.query.filter_by(userid=user_id).first()
        # Perform necessary operations with the test_name and user_id
        if user and mod != True:
            e = User.query.filter_by(email=email).first()
            if e:
                response_data = {
                'status': 'error',
                'message': 'email already exist'
            }
                return jsonify(response_data), 200
            u = User(company_id=user.company_id, email=email, first_name=fn, last_name=ln,
                     role=role, password=pwd)
            com = Company.query.filter_by(companyid=user.company_id).first()
            u.created = datetime.now()
            db.session.add(u)
            db.session.commit()
            response_data = {
                'status': 'success',
                'message': 'User saved successfully'
            }
            try:
                run_time = datetime.now() + timedelta(seconds=10) 
                scheduler.add_job(id=f'send_newuser_mail{pwd}', func=send_newuser_mail, args=(pwd, fn, email, 'luvpascal.ojukwu@yahoo.com', com.company_name), trigger='date', run_date=run_time)
                # send_test_mail(test_day_id, applicant.user_id)
            except:
                return jsonify({'message': 'INFO: An error occured while sending mail'})


            return jsonify(response_data), 200
        else:
            u = User.query.filter_by(userid=moduserid).first()
            if u:
                u.first_name = fn
                u.last_name = ln
                u.email = email
                u.role = role
                db.session.commit()
            
        # On success, you can send a response to refresh the current page
            response_data = {
                'status': 'success',
                'message': 'User saved successfully'
            }

            return jsonify(response_data), 200

    except Exception as e:
        # Handle any exceptions or errors
        error_data = {
            'status': 'error',
            'error': str(e)
        }

        return jsonify(error_data), 500
    return jsonify({
            'status': 'error',
            'error': 'Unauthorized user'
        })
        

@app.route('/userboard/<user_id>', methods=['GET', 'POST'])
@login_required
def userboard(user_id):
    count = 1
    u = User.query.filter_by(userid=user_id).first()
    if not u:
        return jsonify({'error': 'Unauthorized User'}), 401
    if u.role == 'user':
        return jsonify({'error': 'Unauthorized User'}), 401
    q_param = request.form.get('q')
    if q_param == 'name' and request.form['name'] != '':
        q = request.form['name']
        user = User.query.filter(
                (User.email != u.email) &
                (or_(User.first_name.contains(q), User.last_name.contains(q)))
                ).order_by(desc(User.created))
    else:
        user = User.query.filter(User.email != u.email).order_by(desc(User.created))
    if not user:
        return jsonify({'error': 'Unauthorized User'}), 401
    u = User.query.filter_by(userid=user_id).first()
    if not u:
        return jsonify({'error': 'Unauthorized User'}), 401
    
    page = request.args.get("page")
    #localhost:5000/blog?page=7478
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    try:
        pages = user.paginate(page=page, per_page=3)
    except:
        if (user.count() % 3 != 0):
            count =  int((user.count() / 3)) + 1
        else:
            count = (user.count() / 3)
        
        if count <= 0:
            count = 1
        pages = user.paginate(page=count, per_page=3)

    
    return render_template('Userdashboard.html', user=user, i=0, pages=pages,
                           companyname='', user_id=user_id)

    render_template('Userdashboard.html', user_id=user_id)
@app.route('/emailboard/<user_id>', methods=['GET'])
@login_required
def emailboard(user_id):
    count = 1
    u = User.query.filter_by(userid=user_id).first()
    if not u:
        return jsonify({'error': 'Unauthorized User'}), 401
    if u.role == 'user':
        return jsonify({'error': 'Unauthorized User'}), 401
    email = Emailserver.query.order_by(desc(Emailserver.id))
    if not email:
        return jsonify({'error': 'Unauthorized User'}), 401
    u = User.query.filter_by(userid=user_id).first()
    if not u:
        return jsonify({'error': 'Unauthorized User'}), 401
    
    page = request.args.get("page")
    #localhost:5000/blog?page=7478
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    try:
        pages = email.paginate(page=page, per_page=3)
    except:
        if (email.count() % 3 != 0):
            count =  int((email.count() / 3)) + 1
        else:
            count = (email.count() / 3)
        
        if count <= 0:
            count = 1
        pages = email.paginate(page=count, per_page=3)
    return render_template('Emaildashboard.html', email=email, i=0, pages=pages,
                           companyname='', user_id=user_id)


@app.route('/savemail/<user_id>', methods=['POST'])
@jwt_required()
def savemail(user_id):
    try:
        data = request.json
        sender = data.get('sender', '')
        cc = data.get('cc', '')
        pwd = data.get('password', '')
        un = data.get('username', '')
        port = data.get('port', '')
        server = data.get('server', '')
        tls = data.get('TLS', '')
        mod = data.get('mod', '')
        ssl = data.get('SSL', '')
        
        modemailid = data.get('modemailid', '')

        user = User.query.filter_by(userid=user_id).first()
        # Perform necessary operations with the test_name and user_id
        if user and mod != True:
            status = ''
            mails = Emailserver.query.all()
            if len(mails) > 0:
                response_data = {
                'status': 'error',
                'error': 'Mail server already saved, you can only have one mail server settings'
            }
                return jsonify(response_data), 200
            
            if len(mails) == 0:
                status = 'Yes'
            else:
                status = 'No'
            Mail_ = Emailserver(sender=sender,
                            cc=cc,
                            mail_server=server,
                            mail_use_ssl=ssl,
                            mail_use_tls=tls,
                            mail_port=port,
                            username=un,
                            password=pwd,
                            active=status)
            
            db.session.add(Mail_)
            db.session.commit()
            response_data = {
                'status': 'success',
                'message': 'Mail saved successfully'
            }

            return jsonify(response_data), 200
        else:
            u = Emailserver.query.filter_by(emailid=modemailid).first()
            if u:
                u.sender = sender
                u.cc = cc
                u.mail_server = server
                u.mail_port = port
                u.mail_use_tls = tls
                u.mail_use_ssl = ssl
                u.username = un
                u.password = pwd
                db.session.commit()
            
        # On success, you can send a response to refresh the current page
            response_data = {
                'status': 'success',
                'message': 'Mail saved successfully'
            }

            return jsonify(response_data), 200

    except Exception as e:
        # Handle any exceptions or errors
        error_data = {
            'status': 'error',
            'error': str(e)
        }

        return jsonify(error_data), 500
    return jsonify({
            'status': 'error',
            'error': 'Unauthorized user'
        })
        


@app.route('/mainboard/<user_id>', methods=['GET'])
@login_required
def mainboard(user_id):
    user = User.query.filter_by(userid=user_id).first()
    if user:
        com = Company.query.filter_by(companyid=user.company_id).first()
        return render_template('Mainboard.html', company_name=com.company_name, user_id=user_id)
    return jsonify({'error': 'bad request'}), 400

@app.route('/Registrationsuccess/<user_id>', methods=['GET'])
def Registrationsuccess(user_id):
    return render_template('Registrationsuccess.html', user_id=user_id)

@app.route('/get_id/<email>/<pwd>', methods=['POST'])
def get_id(email, pwd):
    
    password_ = hashlib.md5(pwd.encode()).hexdigest()
    user = User.query.filter_by(email=email).first()
    
    if not user or user.password != password_:
        return jsonify({"message": "Invalid username or password"}), 401
    return jsonify({'user_id': user.userid})

@app.route('/signin_post', methods=['POST'])
def signin_post():
    data = request.json
    if not data:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    if 'email' not in data:
        return make_response(jsonify({'error': 'Missing email'}), 400)
    if 'password' not in data:
        return make_response(jsonify({'error': 'Missing password'}), 400)
 
    email = data.get('email')
    pwd = data.get('password')
    remember = data.get('remember')
    password_ = hashlib.md5(pwd.encode()).hexdigest()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Invalid username or password"}), 401
    com = Company.query.filter_by(companyid=user.company_id).first()
    if not user or user.password != password_ or com.confirm != True:
        return jsonify({"message": "Invalid username or password"}), 401
    
    login_user(user, remember=remember)
    access_token = create_access_token(identity=user.email)

    # Set the JWT token as a cookie
    response = jsonify(access_token=access_token)
    response.set_cookie('jwtToken', value=access_token, httponly=False, secure=True, path='/', samesite='Strict')  # Adjust secure=True based on your deployment
    return response
    return render_template('Signin.html')

@app.route('/signup_post', methods=['POST'])
def signup_post():
    #try:
    signup_data = request.json
    company_name = signup_data["company_name"]
    company_website = signup_data["company_website"]
    company_email = signup_data["company_email"]
    company_address = signup_data["company_address"]
    first_name = signup_data["first_name"]
    last_name = signup_data["last_name"]
    email = signup_data["email"]
    password = signup_data["password"]
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Record already exist'})
    company = Company(company_name=company_name, company_email=company_email,
                        company_website=company_website,
                        company_address=company_address)
    db.session.add(company)
    db.session.commit()
    user = User(email=email, password=password, first_name=first_name,
                last_name=last_name, role='admin')
    company.users.append(user)
    db.session.commit()
    send_confirm_mail(email, 'luvpascal.ojukwu@yahoo.com', user.userid, user.last_name + ' ' + user.first_name)
    return jsonify({'user_id': user.userid , 'message': 'Thank you for signing up, please check your email to complete your registration'})
    #""" except:
    #""" return jsonify({'error': 'A error occured please try again '})

@app.route('/testcompanion_confirm/<user_id>', methods=['GET'])
def testcompanion_confirm(user_id):
    user = User.query.filter_by(userid=user_id).first()
    confirm = request.args.get('confirm')
    if user:
        try:
            com = Company.query.filter_by(companyid=user.company_id).first()
            if com.confirm == True:
                pass
                #return jsonify({'error': 'link has expired'})
            if confirm == 'True':
                com.confirm = True
            db.session.commit()
            return render_template('confirmation.html')
        except:
            return jsonify({'error': 'An error occured'})
    return jsonify({'error': 'link has expired'})

@app.route('/resend_confirm_mail/<user_id>', methods=['POST'])
def resend_confirm_mail(user_id):
    u = request.json
    userid = u['user_id']
    if userid  == '' or userid is None:
        return jsonify({'error', 'Unauthorized user'}),  401
    user = User.query.filter_by(userid=userid).first()
    if user:
        send_confirm_mail(user.email, 'luvpascal.ojukwu@yahoo.com', user.userid, user.last_name + ' ' + user.first_name)
        return jsonify({'success': 'success', 'message': 'Confirmation mail sent'})


def send_confirm_mail(recipient_email, admin_email, user_id, fullname):
    html_content = render_template('Confirmreg.html', user_id=user_id, fullname=fullname)
    recipients = [recipient_email, admin_email]
    app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
    app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
    mail = Mail(app)
    msg = Message('Successful - Welcome to TestCompanion', sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
    mail.send(msg)


@app.route('/computescore/<test_day_id>', methods=['POST'])
@jwt_required()
def computescore(test_day_id):
    applicants = Applicanttest.query.filter_by(test_day_id=test_day_id, test_status='pending').all()
    for applicant in applicants:
        correct_answers = 0
        if applicant and applicant.test_status == 'pending':
            teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
            if teststat:
                test = Test.query.filter_by(test_id=teststat.test_id).first()
                if test:
                    questioncount = len(test.questions)
                    user_questions = Userquestion.query.filter_by(user_id=applicant.user_id).all()
                    # Count the number of correct answers
                    for uq in user_questions:
                        ques = Question.query.filter_by(question_id=uq.question_id).first()
                        if ques:
                            if sorted(uq.answer_chosen) == sorted(ques.correct_answer):
                                correct_answers += 1
                    questions = Question.query.filter_by(test_id=teststat.test_id).all()
                    for question in questions:
                        u = Userquestion.query.filter_by(question_id=question.question_id, user_id=applicant.user_id).first()
                        if not u:
                            user_question = Userquestion(question_id=question.question_id,
                                            Qnum=question.Qnum,
                                            user_id=applicant.user_id,
                                            answer_chosen='')
                            db.session.add(user_question)
                            db.session.commit()
                            
                                
                    # Calculate the percentage score
                    percentage_score = (correct_answers / questioncount) * 100

                    # Round the percentage to two decimal places
                    percentage_score = round(percentage_score, 2)
                    applicant.score = percentage_score
                    applicant.test_status = 'completed'
                    if teststat.status != 'taken':
                        teststat.status = 'taken'
                    db.session.commit()
                    try:
                        run_time = datetime.now() + timedelta(seconds=10) 
                        scheduler.add_job(id=f'send_test_mail{test_day_id}', func=send_test_mail, args=(test_day_id, applicant.user_id), trigger='date', run_date=run_time)
                        # send_test_mail(test_day_id, applicant.user_id)
                    except:
                        return jsonify({'message': 'INFO: An error occured while sending mail to ' + applicant.user_email + 'please try again or check that the email is correct'})
    return jsonify({'message': 'All Scores computed successlfully'})

@app.route('/testsummary/<test_id>/<test_day_id>/<user_id>', methods=['GET'])
@login_required
def testsummary(test_id, test_day_id, user_id):
    test = Test.query.filter_by(test_id=test_id).first()
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    user = User.query.filter_by(userid=user_id).first()

    if not test or not teststat or not user:
        return jsonify({'error': 'Unauthorized user'})

    
    allapplicants = Applicanttest.query.filter_by(test_day_id=test_day_id)\
                                        .order_by(Applicanttest.score.desc()).all()
    applicant_data = []

    for app in allapplicants:
        correct_answers = 0
        questions_data = []
        status = 'Not attempted'
        user_questions = Userquestion.query.filter_by(user_id=app.user_id).all()
        qcount = len(user_questions)
        for uq in user_questions:
            if status == 'Not attempted':
                status = 'Completed'
            ques = Question.query.filter_by(question_id=uq.question_id).first()
            if ques:
                imageurl = None
                base_url = os.path.dirname(os.path.abspath(__name__))
                imagstagjpeg = f'image_{ques.question_id}_{test.test_id}.jpeg'
                imagstagpng = f'image_{ques.question_id}_{test.test_id}.png'
                imagstagjpg = f'image_{ques.question_id}_{test.test_id}.jpg'
                img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
                img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
                img_path3 = os.path.join(base_url, 'static/images', imagstagpng)
                k = [img_path1, img_path2, img_path3]
                for path in k:
                    if os.path.exists(path):
                        path = path.split('/')[1:]
                        imageurl = '/' + path[1] + '/' + path[2] + '/' + path[3] 
                        break
                question_text = ques.text
                question_point = 0
                if sorted(uq.answer_chosen) == sorted(ques.correct_answer):
                    correct_answers += 1
                    question_point = 1
                questions_data.append({'text': question_text, 'point': question_point, 'imageurl': imageurl})

        applicant_data.append({
            'name': app.fullname,
            'email': app.user_email,
            'score': f'{app.score}%',
            'status': status,
            'questions': questions_data,
            'marks': f'{correct_answers}/{qcount}'
        })
    return render_template('Testsummary.html', testname=test.test_name, test_id=test_id
                           ,test_day_id=test_day_id, user_id=user_id,  applicants=applicant_data, count=len(allapplicants))

@app.route('/testlist/<test_id>', methods=['GET', 'POST'])
@login_required
def testlist(test_id):
    """test list."""
    count = 1
    start_date = ''
    end_date = ''
    ed = None
    sd = None
    du = None
    q_param = request.form.get('q')
    if q_param == 'date' and request.form['start-date'] != '' and request.form['end-date'] != '':
        start_date = datetime.strptime(request.form['start-date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end-date'], '%Y-%m-%d')
        duration = request.form['duration']
        if duration == '':
            duration = 0
        teststat = Teststat.query.filter_by(test_id=test_id) \
                    .filter(
                        (Teststat.test_date >= start_date) &
                        (Teststat.test_date <= end_date) |
                        (Teststat.duration == int(duration))
                    ) \
                    .order_by((Teststat.test_date.desc()))
        sd = request.form['start-date']
        ed = request.form['end-date']
        du = request.form['duration']
    else:
        teststat = Teststat.query.filter_by(test_id=test_id).order_by(desc(Teststat.test_date))
    if not teststat:
        return jsonify({'error': 'Unauthorized User'}), 401
    test = Test.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({'error': 'Unauthorized User'}), 401
    page = request.args.get("page")
    #localhost:5000/blog?page=7478
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    try:
        pages = teststat.paginate(page=page, per_page=3)
    except:
        if (teststat.count() % 3 != 0):
            count =  int((teststat.count() / 3)) + 1
        else:
            count = (teststat.count() / 3)
    
        if count <= 0:
            count = 1
        pages = teststat.paginate(page=count, per_page=3)

    
    return render_template('Testlist.html', teststat=teststat, i=0, pages=pages,
                           test_id=test_id, testname=test.test_name, user_id=test.userid, sd=sd, ed=ed, du=du)


@app.route('/login', methods=['GET'])
def login():
    """Login user."""
    data = {"email":"pascallino90@gmail.com", "password":"fake pwd"}
    if not data:
        return make_response(jsonify({'error': 'Not a JSON'}), 400)
    if 'email' not in data:
        return make_response(jsonify({'error': 'Missing email'}), 400)
    if 'password' not in data:
        return make_response(jsonify({'error': 'Missing password'}), 400)

    email = data.get('email')
    pwd = data.get('password')
    password_ = hashlib.md5(pwd.encode()).hexdigest()
    user = User.query.filter_by(email=email).first()

    if not user or user.password != password_:
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.email)

    # Set the JWT token as a cookie
    response = jsonify(access_token=access_token)
    response.set_cookie('jwtToken', value=access_token, httponly=False, secure=True, path='/', samesite='Strict')  # Adjust secure=True based on your deployment
    login_user(user, remember=False)
    return response

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')
    # return redirect(url_for('index'))


@app.route('/post_selection', methods=['POST'])
@jwt_required()
def post_selection():
    json_data = request.get_json()
    if not json_data:
        return make_response(jsonify({'error': 'Not a JSON'}), 400) 
    else:
        userId = json_data['user_id']
        appcheck = Applicanttest.query.filter_by(user_id=userId, test_status='completed' ).first()
        if appcheck:
            return render_template('Timeout.html')
        currentQuestionId = json_data['question_id']
        selectedOptions = json_data['option_numbers']
        question_number = int(json_data['question_number'])
        user_question = Userquestion.query.filter_by(question_id=currentQuestionId, user_id=userId).first()
        correct_str = ''
        for c in range(len(selectedOptions)):
            if c < len(selectedOptions) - 1:
                correct_str += selectedOptions[c] + ','
            else:
                correct_str += selectedOptions[c] 
        if user_question:
            user_question.created_date = datetime.now()
            #user_question.answer_chosen = selectedOption
            user_question.answer_chosen = correct_str
            db.session.commit()
            return jsonify({'message': 'posted'})  
        else:
            user_question = Userquestion(question_id=currentQuestionId,
                                         Qnum=question_number,
                                         user_id=userId,
                                         answer_chosen=correct_str)
            db.session.add(user_question)
            db.session.commit()
            return jsonify({'message': 'posted'})  
#get question couint 
@app.route('/question_count/<test_day_id>/<user_id>', methods=['GET'])
@jwt_required()
def question_count(test_day_id, user_id):
    test = Teststat.query.filter_by(test_day_id=test_day_id).first()
    applicantdata = Applicanttest.query.filter_by(user_id=user_id).first()
    if not applicantdata:
        return jsonify({'error': 'user not found'}), 404
    cur_time = datetime.now()
    time_span = timedelta(seconds=(test.duration  * 60) + 8)
    exp_time = applicantdata.start_date + time_span
    if exp_time < cur_time:
        return jsonify({'message': 'Test Expired'})
    
    question =  Question.query.filter_by(test_id=test.test_id).all()
    if question:
        #cur_time = datetime.now()
        #time_span = timedelta(seconds=test.duration)
        #duration = session_dict['created_at'] + time_span
        #if exp_time < cur_time:
        return jsonify({'count': len(question), 'duration': (((exp_time - cur_time).total_seconds() + 1)/60)})
    else:
        return jsonify({'error': 'Question not found'}), 404
#redirect the use to log out page
def validate_and_format_datetime(date, time):
    try:
        # Combine date and time into a datetime object
        time = f"{time}:00"
        combined_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        return combined_datetime
    except ValueError:
        return None
@app.route('/dashboard/<user_id>', methods=['GET', 'POST'])
@login_required
def dashboard(user_id):
    # get the company id through the user id
    #use it to filter all users for the company
    count = 1
    start_date = ''
    end_date = ''
    ed = None
    sd = None
    q_param = request.form.get('q')
    if q_param == 'date' and request.form['start-date'] != '' and request.form['end-date'] != '':
        start_date = datetime.strptime(request.form['start-date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end-date'], '%Y-%m-%d')
        test = Test.query.filter_by(userid=user_id)\
            .filter(and_(Test.created >= start_date, Test.created <= end_date))\
            .order_by(Test.created.desc())
        sd = request.form['start-date']
        ed = request.form['end-date']
    else:
        test = Test.query.filter_by(userid=user_id).order_by(desc(Test.created))
    if not test:
        return jsonify({'error': 'Unauthorized User'}), 401
    user = User.query.filter_by(userid=user_id).first()
    if not user:
        return jsonify({'error': 'Unauthorized User'}), 401
    users = User.query.all()
    page = request.args.get("page")
    #localhost:5000/blog?page=7478
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    try:
        pages = test.paginate(page=page, per_page=3)
    except:
        if (test.count() % 3 != 0):
            count =  int((test.count() / 3)) + 1
        else:
            count = (test.count() / 3)
        
        if count <= 0:
            count = 1
        pages = test.paginate(page=count, per_page=3)
    return render_template('Dashboard.html', test=test, i=0, pages=pages,
                           companyname='', user=user, users=users, user_id=user_id, sd=sd, ed=ed)

@app.route('/applicant/<test_day_id>', methods=['GET'])
def applicant(test_day_id):
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if teststat:
        return render_template('applicant.html', duration=teststat.duration)
    return jsonify({'error': 'cant load page'})

@app.route('/savetest/<user_id>', methods=['POST'])
@jwt_required()
def savetest(user_id):
    try:
        data = request.get_json()
        test_name = data.get('testname', '')
        user = User.query.filter_by(userid=user_id).first()
        # Perform necessary operations with the test_name and user_id
        if user and test_name != '':
            test = Test(test_name=test_name)
            test.created = datetime.now()
            user.tests.append(test)
            db.session.commit()
        # On success, you can send a response to refresh the current page
            response_data = {
                'status': 'success',
                'message': 'Test saved successfully'
            }

            return jsonify(response_data), 200

    except Exception as e:
        # Handle any exceptions or errors
        error_data = {
            'status': 'error',
            'error': str(e)
        }

        return jsonify(error_data), 500
    return jsonify({
            'status': 'error',
            'error': 'Unauthorized user'
        })

@app.route('/deletemaintest/<test_id>', methods=['POST'])
@jwt_required()
def deletemaintest(test_id):
    data = request.get_json()
    test_id = data['test_id']
    test = Test.query.filter_by(test_id=test_id).first()
    if test:
        Q = Question.query.filter_by(test_id=test_id).all()
        if Q:
            base_url = os.path.dirname(os.path.abspath(__name__))
            for q in Q:
                uq = Userquestion.query.filter_by(question_id=q.question_id).all()
                if uq:
                    for uu in uq:
                        db.session.delete(uu)
                    db.session.commit()  
                for o in q.options:
                    db.session.delete(o)
                db.session.delete(q)
                imagstagjpeg = f'image_{q.question_id}_{test_id}.jpeg'
                imagstagpng = f'image_{q.question_id}_{test_id}.png'
                imagstagjpg = f'image_{q.question_id}_{test_id}.jpg'
                img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
                img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
                img_path3 = os.path.join(base_url, 'static/images', imagstagpng)
                k = [img_path1, img_path2, img_path3]
                for path in k:
                    if os.path.exists(path):
                         os.remove(path)
                db.session.commit()

        teststat = Teststat.query.filter_by(test_id=test_id).all()
        if teststat:
            for t in teststat:
                for app in t.applicanttests:
                    db.session.delete(app)
                db.session.delete(t)
                db.session.commit()
        db.session.delete(test)
        db.session.commit()
        # t = Test.query.filter_by(userid=user_id).all()
        return jsonify({'message': 'All test records have been deleted', 'status': 'success'})
    return jsonify({'message': 'An error occured while performing this operation','status': 'error, not a valid test'})

@app.route('/resendmailget/<test_day_id>/<user_id>', methods=['GET'])
@login_required
def resendmailget(test_day_id, user_id):
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if not teststat:
        return jsonify({'error': 'Unauthorized user'})
    
    return render_template('Resendemail.html', test_id=teststat.test_id, test_day_id=test_day_id, user_id=user_id)
@app.route('/resendmailpost/<test_day_id>/<user_id>', methods=['POST'])
@jwt_required()
def resendmailpost(test_day_id, user_id):
    user = User.query.filter_by(userid=user_id).first()
    if not user:
        return jsonify({'error': 'Unauthorized user'})
    com = Company.query.filter_by(companyid=current_user.company_id).first()
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if not teststat:
        return jsonify({'error': 'Unauthorized user'})
    test = Test.query.filter_by(test_id=teststat.test_id).first()
    j = request.get_json()
    count = j.get('count', 0)
    for i in range(1, count + 1):
        fullname = j.get(f'user_{i}', '')['username']
        email = j.get(f'user_{i}', '')['email']
        applicant = Applicanttest.query.filter_by(test_day_id=teststat.test_day_id, user_email=email).first()
        if not applicant:
            applicant = Applicanttest(user_email=email, start_date=None, fullname=fullname)
            teststat.applicanttests.append(applicant)
            try:
                # send_applicantmail(email, fullname, teststat.test_date, teststat.duration, test.test_name, 'sample company', 'Test lab',
                                # user.email, user.first_name, applicant.user_id, applicant.secret_key)
                run_time = datetime.now() + timedelta(seconds=7) 
                # send_applicantmail(email, fullname, formatted_datetime, duration, test.test_name, 'sample company', 'Test lab',
                #                user.email, user.first_name, applicant.user_id, applicant.secret_key)
                scheduler.add_job(id=f'send_applicantmail{email}', func=send_applicantmail, args=(email, fullname, teststat.test_date, teststat.duration, test.test_name, com.company_name, com.company_address,
                                user.email, user.first_name, applicant.user_id, applicant.secret_key), trigger='date', run_date=run_time)

                db.session.commit()
            except:
                  return jsonify({'error': 'Mail sending error, check internet connection or check incorrect email address and try again'})
            
    
    db.session.commit()
    return jsonify({'message': 'Saved successfully'})
@app.route('/deletetestday/<test_day_id>', methods=['POST'])
@jwt_required()
def deletetestday(test_day_id):
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if teststat:
        if teststat.status != 'pending':
            return jsonify({'error': 'WARNING: Test has been taken, cannot be deleted'})
        test = Test.query.filter_by(test_id=teststat.test_id).first()
        applicants = Applicanttest.query.filter_by(test_day_id=test_day_id, test_status='pending').all()
        for a in applicants:
            run_time = datetime.now() + timedelta(seconds=10) 
            scheduler.add_job(id=f'send_canceltest_mail{a.user_id}', func=send_canceltest_mail, args=(a.fullname, test.test_name , a.user_email), trigger='date', run_date=run_time)        

    applicant = Applicanttest.query.filter_by(test_day_id=test_day_id).all()
    if applicant:
        for ap in applicant:
            db.session.delete(ap)
            db.session.commit()
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if teststat:
        db.session.delete(teststat)
        db.session.commit()
        return jsonify({'message': 'Test deleted successfully'})
    else:
         return jsonify({'error': 'Unauthorized User'})
@app.route('/Addtestuserpost/<test_id>/<user_id>', methods=['POST'])
@jwt_required()
def Addtestuserpost(test_id, user_id):
    user = User.query.filter_by(userid=user_id).first()
    if not user:
        return jsonify({'error': 'Unauthorized user'})
    com = Company.query.filter_by(companyid=current_user.company_id).first()
    test = Test.query.filter_by(test_id=test_id).first()
    if not test:
        return jsonify({'error': 'Unauthorized user'})
    question = Question.query.filter_by(test_id=test_id).first()
    if not question:
        return jsonify({'error': 'INFO: Please add questions to the test, before your proceed'})
    j = request.get_json()
    input_date = j.get('date', '')
    input_time = j.get('time', '')
    count = j.get('count', '')
    duration = j.get('duration', '')
    formatted_datetime = validate_and_format_datetime(input_date, input_time)
    if  formatted_datetime < datetime.now():
        return jsonify({'message': 'Date/Time is in the past'})
    teststat = Teststat.query.filter_by(test_id=test_id, test_date=formatted_datetime).first()
    if not teststat:
        teststat =  Teststat(test_date= formatted_datetime, duration=duration)
        test.teststats.append(teststat)
    for i in range(1, count + 1):
        fullname = j.get(f'user_{i}', '')['username']
        email = j.get(f'user_{i}', '')['email']
        applicant = Applicanttest.query.filter_by(test_day_id=teststat.test_day_id, user_email=email).first()
        if not applicant:
            applicant = Applicanttest(user_email=email, start_date=None, fullname=fullname)
            teststat.applicanttests.append(applicant)
            try:
                run_time = datetime.now() + timedelta(seconds=7) 
                # send_applicantmail(email, fullname, formatted_datetime, duration, test.test_name, 'sample company', 'Test lab',
                #                user.email, user.first_name, applicant.user_id, applicant.secret_key)
                scheduler.add_job(id=f'send_applicantmail{email}', func=send_applicantmail, args=(email, fullname, formatted_datetime, duration, test.test_name, com.company_name, com.company_address,
                                user.email, user.first_name, applicant.user_id, applicant.secret_key), trigger='date', run_date=run_time)
                db.session.commit()
            except Exception as e:
                return jsonify({'error': str(e)})
                #return jsonify({'error': 'Mail sending error, check for incorrect email address and try again'})
            
    
    db.session.commit()
    return jsonify({'message': 'Email Sent successfully'})
def send_applicantmail(recipient_email, applicantname, testdate, duration, testName, yourCompanyName,
                       companyAddress, admin_email, admin_name, user_id, key):
    with app.app_context():
        html_content = render_template('email_template.html', yourCompanyName=yourCompanyName, companyAddress=companyAddress,
                                        applicantname=applicantname, testdate=testdate, duration=duration, admin_name=admin_name,
                                        admin_email=admin_email, testName=testName, user_id=user_id, key=key)
        recipients = [recipient_email, admin_email]
        mailstat = get_mail_status()
        if mailstat and mailstat.active == 'Yes':
            app.config['MAIL_SERVER'] = mailstat.mail_server
            app.config['MAIL_PORT'] = mailstat.mail_port
            app.config['MAIL_USE_TLS'] = mailstat.mail_use_tls
            app.config['MAIL_USE_SSL'] = mailstat.mail_use_ssl
            app.config['MAIL_USERNAME'] = mailstat.username
            app.config['MAIL_PASSWORD'] = mailstat.password
        else:
            app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USE_SSL'] = False
            app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
            app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
        mail = Mail(app)
        msg = Message(testName, sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
        mail.send(msg)
@app.route('/Addtestuser/<test_id>/<user_id>', methods=['GET'])
@login_required
def Addtestuser(test_id, user_id):
    test = Test.query.filter_by(test_id=test_id, userid=user_id).first()
    if test:
        return render_template('Addtestuser.html', test_id=test_id, user_id=user_id)
    return jsonify({'error': 'Unauthorized user'})

@app.route('/rescheduletest/<test_day_id>', methods=['GET'])
@login_required
def rescheduletestget(test_day_id):
    teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if teststat:
        test = Test.query.filter_by(test_id=teststat.test_id).first()
        return render_template('rescheduletest.html',
                            test_day_id=test_day_id, testname=test.test_name, test_id=test.test_id)
    else:
        return jsonify({'error': 'Unauthorized User'})
@app.route('/rescheduletestpost/<test_day_id>', methods=['POST'])
@jwt_required()
def rescheduletestpost(test_day_id):
    # Get the date and time from the POST request
    # Get the JSON data from the POST request
    data = request.get_json()

    # Access the 'date' and 'time' fields from the JSON data
    input_date = data.get('date')
    input_time = data.get('time')
    if input_date is None or input_time is None:
        return jsonify({'error': 'Date or time is missing'}), 400

    # Validate and format the datetime
    formatted_datetime = validate_and_format_datetime(input_date, input_time)

    if formatted_datetime is None:
        return jsonify({'error': 'Invalid date or time format'}), 400
    
    if formatted_datetime < datetime.today():
        flash('Datetime should be in the future or todays date')
        return jsonify({'error': 'Datetime should be in the future or todays date'})
        #return redirect(url_for('rescheduletestget', test_day_id=test_day_id))
    # At this point, 'formatted_datetime' is a valid datetime
    # Save it to the database (replace this with your actual database saving logic)
    ts = Teststat.query.filter_by(test_day_id=test_day_id).first()
    if ts.status == 'taken':
          return jsonify({'error': 'Test already taken, cant be rescheduled'})
    if ts.status != 'taken':
        test = Test.query.filter_by(test_id=ts.test_id).first()
        ts.test_date = formatted_datetime
        db.session.commit()
        applicants = Applicanttest.query.filter_by(test_day_id=test_day_id, test_status='pending').all()
        for a in applicants:
            run_time = datetime.now() + timedelta(seconds=10) 
            scheduler.add_job(id=f'send_reschedule_mail{a.user_id}', func=send_reschedule_mail, args=(a.fullname, formatted_datetime, test.test_name , a.user_email), trigger='date', run_date=run_time)        
        # Return a success response
        flash('Test Rescheduled successfully')
        # return redirect(url_for('rescheduletestget', test_day_id=test_day_id))
        return jsonify({'message': 'Test Rescheduled successfully'})

def send_canceltest_mail(name, testname, recipient_email):
    with app.app_context():
        html_content = render_template('Testcancel.html', name=name, testname=testname, recipient_email=recipient_email)
        recipients = [recipient_email]
        app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
        app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
        mail = Mail(app)
        msg = Message('Test Cancellation Notice', sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
        mail.send(msg)

def send_reschedule_mail(name, new_test_date, testname, recipient_email):
    with app.app_context():
        html_content = render_template('Testrechedule.html', name=name, new_test_date=new_test_date,
                                        testname=testname, recipient_email=recipient_email)
        recipients = [recipient_email]
        app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
        app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
        mail = Mail(app)
        msg = Message('Test Reschedule Notification', sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
        mail.send(msg)

def send_newuser_mail(pwd, fn, recipient_email, email, companyname):
    with app.app_context():
        html_content = render_template('Usercreated.html', password=pwd, name=fn,
                                        contactemail=email, companyname=companyname)
        recipients = [recipient_email]
        app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
        app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
        mail = Mail(app)
        msg = Message('New Member Registration - TestCompanion', sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
        mail.send(msg)
        
def send_test_mail(test_day_id, user_id):
    with app.app_context():
        applicant = Applicanttest.query.filter_by(user_id=user_id).first()
        teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
        test = Test.query.filter_by(test_id=teststat.test_id).first()
        user = User.query.filter_by(userid=test.userid).first()
        com = Company.query.filter_by(companyid=user.company_id).first()
        recipient_email = applicant.user_email
        # username = "John Doe"
        # company = "Sample Company"
        yourCompanyName = com.company_name
        companyAddress = com.company_address
        testScore = applicant.score
        testName = test.test_name
        html_content = render_template('testsubmitted.html', yourCompanyName=yourCompanyName, companyAddress=companyAddress,
                                        testName=testName, testScore=testScore, applicant=applicant.fullname)
        recipients = [recipient_email, 'pascallino90@gmail.com']
        mailstat = get_mail_status()
        if mailstat and mailstat.active == 'Yes':
            app.config['MAIL_SERVER'] = mailstat.mail_server
            app.config['MAIL_PORT'] = mailstat.mail_port
            app.config['MAIL_USE_TLS'] = mailstat.mail_use_tls
            app.config['MAIL_USE_SSL'] = mailstat.mail_use_ssl
            app.config['MAIL_USERNAME'] = mailstat.username
            app.config['MAIL_PASSWORD'] = mailstat.password
        else:
            app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USE_SSL'] = False
            app.config['MAIL_USERNAME'] = 'luvpascal.ojukwu@yahoo.com'
            app.config['MAIL_PASSWORD'] = 'nvfolnadxvdepvxk'
        mail = Mail(app)
        msg = Message(testName +' GRADED', sender='luvpascal.ojukwu@yahoo.com', recipients=recipients, html=html_content)
        mail.send(msg)


@app.route('/Timeout/<test_day_id>/<user_id>', methods=['GET'])
def Timeout(test_day_id, user_id):
    questioncount = 0
    correct_answers = 0
    applicant = Applicanttest.query.filter_by(user_id=user_id).first()
    if not applicant:
        return jsonify({'error': 'Unauthorized User'})
    if applicant and applicant.test_status == 'pending':
        teststat = Teststat.query.filter_by(test_day_id=test_day_id).first()
        if teststat:
            test = Test.query.filter_by(test_id=teststat.test_id).first()
            if test:
                questioncount = len(test.questions)
                user_questions = Userquestion.query.filter_by(user_id=user_id).all()
                # Count the number of correct answers
                for uq in user_questions:
                    ques = Question.query.filter_by(question_id=uq.question_id).first()
                    if ques:
                        if sorted(uq.answer_chosen) == sorted(ques.correct_answer):
                            correct_answers += 1
                questions = Question.query.filter_by(test_id=teststat.test_id).all()
                for question in questions:
                    u = Userquestion.query.filter_by(question_id=question.question_id, user_id=user_id).first()
                    if not u:
                        user_question = Userquestion(question_id=question.question_id,
                                        Qnum=question.Qnum,
                                        user_id=user_id,
                                        answer_chosen='')
                        db.session.add(user_question)
                        db.session.commit()
                        
                            
                # Calculate the percentage score
                percentage_score = (correct_answers / questioncount) * 100

                # Round the percentage to two decimal places
                percentage_score = round(percentage_score, 2)
                applicant.score = percentage_score
                applicant.test_status = 'completed'
                if teststat.status != 'taken':
                    teststat.status = 'taken'
                db.session.commit()
                try:
                    run_time = datetime.now() + timedelta(seconds=10) 
                    scheduler.add_job(id=f'send_test_mail{user_id}', func=send_test_mail, args=(test_day_id, user_id), trigger='date', run_date=run_time)
                except:
                    return jsonify({'message': 'INFO: An error occured while sending mail to ' + applicant.user_email + 'please try again or check that the email is correct'})

                # send_test_mail(test_day_id, user_id)
    return render_template('Timeout.html', test_day_id=test_day_id)

#fetch question for the user
@app.route('/get_question/<int:question_num>/<test_day_id>/<user_id>', methods=['GET'])
@jwt_required()
def get_question(question_num, test_day_id, user_id):
    # Check if the question number exists in the data
    appcheck = Applicanttest.query.filter_by(user_id=user_id, test_status='completed' ).first()
    if appcheck:
        return render_template('Timeout.html')
    test = Teststat.query.filter_by(test_day_id=test_day_id).first()
    applicantdata = Applicanttest.query.filter_by(user_id=user_id).first()
    if not applicantdata:
        return jsonify({'error': 'user not found'}), 404
    cur_time = datetime.now()
    time_span = timedelta(seconds=(test.duration  * 60) + 8)
    exp_time = applicantdata.start_date + time_span
    if exp_time < cur_time:
        return jsonify({'message': 'Test Expired'})
    Ques_data = {'options': {}}  # Initialize options as an empty dictionary
    #Ques_data['duration'] = cur_time - exp_time
    Ques_data['selectedOptions'] = []
    user_question = Userquestion.query.filter_by(user_id=user_id, Qnum=str(question_num)).first()
    if user_question:
        if len(user_question.answer_chosen) == 1:
             Ques_data['selectedOptions'] = [user_question.answer_chosen]
        else:
            Ques_data['selectedOptions'] = user_question.answer_chosen.split(',')
    
    question = Question.query.filter_by(Qnum=question_num, test_id=test.test_id).first()
    if question:
        base_url = os.path.dirname(os.path.abspath(__name__))
        imagstagjpeg = f'image_{question.question_id}_{test.test_id}.jpeg'
        imagstagpng = f'image_{question.question_id}_{test.test_id}.png'
        imagstagjpg = f'image_{question.question_id}_{test.test_id}.jpg'
        img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
        img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
        img_path3 = os.path.join(base_url, 'static/images', imagstagpng)
        k = [img_path1, img_path2, img_path3]
        for path in k:
            if os.path.exists(path):
                path = path.split('/')[1:]
                Ques_data['imageurl'] = '/' + path[1] + '/' + path[2] + '/' + path[3] 
                break
        Ques_data['Question'] = question.text
        Ques_data['question_id'] = question.question_id
        # Retrieve options and sort by Opnum in ascending order
        options = Option.query.filter_by(question_id=question.question_id).order_by(asc(Option.Opnum)).all()

        for option in options:
            Ques_data['options'][option.Opnum] = option.text

        return jsonify(Ques_data)
    else:
        return jsonify({'error': 'Question not found'}), 404

@app.route('/get_data/<test_id>/<user_id>', methods=['GET'])
@jwt_required()
def get_data(test_id, user_id):
    json_data = {}
    countquestion = 0
    q = Question.query.filter_by(test_id=test_id).order_by(Question.Qnum.asc()).all()
    for question in q:
        countquestion += 1
        countOpt = 0
        id = question.question_id
        qu = f"question_text_{question.Qnum}-{id}"
        img = f"image_{question.question_id}"
        base_url = os.path.dirname(os.path.abspath(__name__))
        imagstagjpeg = f"image_{question.question_id}_{test_id}.jpeg"
        imagstagjpg = f"image_{question.question_id}_{test_id}.jpg"
        imagstagpng = f"image_{question.question_id}_{test_id}.png"
        img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
        img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
        img_path3 = os.path.join(base_url, 'static/images', imagstagpng)

        if os.path.exists(img_path1):
            json_data[img] = imagstagjpeg
        elif os.path.exists(img_path2):
            json_data[img] = imagstagjpg
        elif os.path.exists(img_path3):
            json_data[img] = imagstagpng
        #json_data[img] = question.image_path
        json_data[qu] = question.text
        opts = Option.query.order_by(Option.Opnum.asc()).filter_by(question_id=id).all()
        for option in opts:
            option_key = f"option_text_{question.Qnum}_{option.Opnum}"
            json_data[option_key] = option.text
        correct_key = f"correct_option_{question.Qnum}"
        lst = []
        if len(question.correct_answer) > 1:
            lst = question.correct_answer.split(',')
        else:
            lst.append(question.correct_answer)
        json_data[correct_key] = lst
        json_data['Lnum'] = question.Qnum
    return jsonify(json_data)

@app.route('/get_test/<user_id>', methods=['GET'])
def get_test(user_id):
    tests = Test.query.filter_by(userid=user_id).order_by(desc(Test.created)).all()
    if tests:
        test_names = [{'id': test.test_id, 'name': test.test_name, 'created': test.created.strftime('%m/%d/%Y %I:%M:%S %p')} for test in tests]
        return jsonify(test_names)
    else:
        return jsonify({'error': 'No tests found'})
    
@app.route('/posttest_getquestions', methods=['POST'])
@jwt_required()
def posttest_getquestions():
    data = request.json
    new = data['new_test_id']
    old = data['old_test_id']
    newtest = Test.query.filter_by(test_id=new).first()
    oldtest = Test.query.filter_by(test_id=old).first()
    if len(oldtest.questions) <= 0:
         response_data = {
                'status': 'success',
                'message': 'No questions found for the selected test'
            }
         return jsonify(response_data)
    else:
        for ques in oldtest.questions:
            q = Question(text=ques.text, Qnum=ques.Qnum, correct_answer=ques.correct_answer
                        )
            newtest.questions.append(q)
            db.session.commit()
            for op in ques.options:
                o = Option(text=op.text, Opnum=op.Opnum)
                q.options.append(o)
                db.session.commit()
        response_data = {
                    'status': 'success',
                    'message': 'Questions imported successfully'
                }
        return jsonify(response_data)
            
            

@app.route('/editquestion/<test_id>/<user_id>', methods=['GET'])
def editquestion(test_id, user_id):
    test = Test.query.filter_by(test_id=test_id).first()
    if test:
        teststat = Teststat.query.filter_by(test_id=test_id, status='taken').all()
        if teststat:
            for testday in teststat:
                applicant = Applicanttest.query.filter_by(test_day_id=testday.test_day_id, test_status='pending').first()
                if applicant:
                    message = f"for test with duration: {testday.duration} minutes \n and  test date: {testday.test_date}"
                    return render_template('computescoremessage.html', message=message, user_id=user_id)
        return render_template('editquestion.html', test_id=test_id, testname=test.test_name, user_id=user_id)
    return jsonify({'error': 'Unauthorized user'})
@app.route('/authenticate_applicant/<user_id>/<secret_key>', methods=['POST'])
def authenticate_applicant(user_id, secret_key):
    applicant = Applicanttest.query.filter_by(user_id=user_id).first()
    if not applicant:
        return jsonify({'error': 'Unauthorized User'})
    teststat = Teststat.query.filter_by(test_day_id=applicant.test_day_id).first()
    if datetime.now() < teststat.test_date:
        return jsonify({'error': 'Test hasnt been approved yet'})
    expires_in = timedelta(days=1)
    user_id = user_id + secret_key
    access_token = create_access_token(user_id, expires_in)
    # Set the JWT token as a cookie
    response = jsonify(access_token=access_token)
    response.set_cookie('UserTestToken', value=access_token, httponly=False, secure=True, path='/', samesite='Strict')  # Adjust secure=True based on your deployment
    return response

@app.route('/taketest/<user_id>/<key>', methods=['GET'])
def taketest(user_id, key):
    #remember to set this token on the start page for the test
    # an api will veryfy the access token then open the main 
    # test page
    applicant = Applicanttest.query.filter_by(user_id=user_id).first()
    if not applicant:
        return jsonify({'error': 'Unauthorized User'})
    teststat = Teststat.query.filter_by(test_day_id=applicant.test_day_id).first()
    if datetime.now() < teststat.test_date:
        return jsonify({'error': 'Test hasnt been approved yet'})
    if applicant and applicant.test_status == 'completed':
        redirect_url = url_for('Timeout', test_day_id=applicant.test_day_id, user_id=applicant.user_id)
        return redirect(redirect_url)
    if user_id == applicant.user_id and key == applicant.secret_key:
        # Set a custom expiration time (e.g., 7 days)
        #expires_in = timedelta(days=1)
        #access_token = create_access_token(user_id, expires_in)
        # Set the JWT token as a cookie
        #response = jsonify(access_token=access_token)
        #response.set_cookie('UserTestToken', value=access_token, httponly=False, secure=True, path='/', samesite='Strict')  # Adjust secure=True based on your deployment
        #sreturn response
        if applicant.started != 'True':
            applicant.started = True
        if not applicant.start_date:
            applicant.start_date = datetime.now()
        db.session.commit()
        return render_template('taketest.html', test_day_id=teststat.test_day_id,
                               user_id=user_id, test_id=teststat.test_id)
    else:
        return jsonify({'error': 'Not Authorized'})  

@app.route('/question/<test_id>/<user_id>', methods=['GET'])
def question_get(test_id, user_id):
    test = Test.query.filter_by(test_id=test_id).first()
    return render_template('question.html', test_id=test_id, user_id=user_id, testname=test.test_name)
@app.route('/question_post_delete', methods=['POST'])
@jwt_required()
def question_post_delete():
    base_url = os.path.dirname(os.path.abspath(__name__))
    # Handle the DELETE request
    # This example assumes 'hash' is a parameter passed in the request
    id = request.args.get('hash', '')
    # Perform deletion logic based on the hash value
    # Adjust this part based on your specific requirements
    # Example: Delete the question with a specific hash
    uq = Userquestion.query.filter_by(question_id=id).first()
    if uq:
        return jsonify({'error': 'WARNING: The question has already been taken by applicants, cant be deleted'})
    question = Question.query.filter_by(question_id=id).first()
    if question:
        opts = Option.query.filter_by(question_id=id).all()
        for opt in opts:
            db.session.delete(opt)
        ques = Question.query.filter_by(question_id=id).first()
        if ques is not None:
            try:
                imagstagjpeg = f"image_{ques.question_id}_{ques.test_id}.jpeg"
                imagstagjpg = f"image_{ques.question_id}_{ques.test_id}.jpg"
                imagstagpng = f"image_{ques.question_id}_{ques.test_id}.png"
                img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
                img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
                img_path3 = os.path.join(base_url, 'static/images', imagstagpng)
                k = [img_path1, img_path2, img_path3]
                for path in k:
                    if os.path.exists(path):
                            os.remove(path)
            except:
                pass
            db.session.delete(ques)
        db.session.commit()
        return jsonify({'message': 'Question deleted sucessfully'})
    return jsonify({'error': 'Nothing to delete'})
@app.route('/question_post', methods=['POST'])
@jwt_required()
def question_post():
    args = ''
    try:
     args =  request.args.get('hash', '')
    except:
        args = ''
    if request.method == 'POST' and args == '':
        json_data = request.get_json()
        data_dict = json_data
        test_id = data_dict.get('test_id', '')
        q = None
        count = 0
        for key, value in data_dict.items():
            k = str(key)
            key = k.split('-')[0]
            if key.startswith("question_text_"):
                count += 1
                id = k.split('-')[1]
                # Deleting existing question and options
                opts = Option.query.filter_by(question_id=id).all()
                for opt in opts:
                    db.session.delete(opt)
                    db.session.commit()
                ques = Question.query.filter_by(question_id=id).first()
                if ques:
                    db.session.delete(ques)
                    db.session.commit()
                num = key.split("_")[-1]  # Extract the num from the key
                option_key = f"option_text_{num}"
                correct_key = f"correct_option_{num}[]"
                if data_dict.get(correct_key, "") == '':
                    correct_key = f"correct_option_{num}"
                question_text = value.strip() 
                if question_text == '':
                    continue
                correct_option = data_dict.get(correct_key, "")
                correct_str = ''
                for c in range(len(correct_option)):
                    if c < len(correct_option) - 1:
                        correct_str += correct_option[c] + ','
                    else:
                        correct_str += correct_option[c] 
                test = Test.query.filter_by(test_id=test_id).first()
                q = Question(question_id=id, text=question_text,
                             Qnum=count, correct_answer=correct_str)
                test.questions.append(q)
                #db.session.add(test)
                db.session.commit()
                # Adding new options
                try:
                    for i in range(10):
                        option_text = data_dict.get(f"{option_key}_{i}", "")
                        """ if isinstance(option_text, list):
                            option_text  = option_text[0] """
                        if option_text != '':
                            o = Option(text=option_text ,
                                       Opnum=i, question_id=id)
                            q.options.append(o)
                            db.session.commit()
                except (KeyError, IndexError) as e:
                    pass

        # Committing changes after all modifications
        



        # Process the JSON data as needed
        # Respond with JSON (optional)
        ques_count = Question.query.filter_by(test_id=test_id).all()
        text = f"Total Question(s) is now {len(ques_count)}, Question data saved successfully"
        response_data = {'status': 'success', 'message': text}
        return jsonify(response_data)
    else:
        response_data = {'status': 'error', 'error': f'error saving question'}
        return jsonify(response_data) 
    return jsonify({'status': 'error', 'message': 'Invalid request method'}), 400

@app.route('/uploadimages/<test_id>', methods=['POST'])
@jwt_required()
def uploadimages(test_id):
    base_url = os.path.dirname(os.path.abspath(__name__))
    ques = Question.query.filter_by(test_id=test_id).all()
    for q in ques:
        try:
            file_key = f'image_{q.question_id}_{test_id}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    file_extension = os.path.splitext(file.filename)[1]
                    if file_extension == '.jpg' or file_extension == '.png' or file_extension == '.jpeg':
                        new_filename = f'image_{q.question_id}_{test_id}{file_extension}'
                        imagstagjpeg = f'image_{q.question_id}_{test_id}.jpeg'
                        imagstagpng = f'image_{q.question_id}_{test_id}.png'
                        imagstagjpg = f'image_{q.question_id}_{test_id}.jpg'
                        img_path1 = os.path.join(base_url, 'static/images', imagstagjpeg)
                        img_path2 = os.path.join(base_url, 'static/images', imagstagjpg)
                        img_path3 = os.path.join(base_url, 'static/images', imagstagpng)
                        k = [img_path1, img_path2, img_path3]
                        for path in k:
                            if os.path.exists(path):
                                    os.remove(path)
                        # Save the file with the new filename
                        file.save(os.path.join(base_url, 'static/images', new_filename))

                    # Update the database with the new filename
        except Exception as e:
            print(f"Error processing file {file_key}: {str(e)}")
            continue
    response_data = {'status': 'success', 'message': 'Images uploaded successfully'}
    return jsonify(response_data)

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True, host='0.0.0.0', port=5001)