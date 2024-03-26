TestCompanion Web App
Welcome to TestCompanion! This platform provides you with a range of powerful features to manage and customize your experience. Explore the following sections to make the most out of the application:

Features
User Management
Efficiently manage user accounts.
Designate roles and organize users as per your system's requirements.
Users are the members who can create and manage their candidates and administer tests to them accordingly.
Mail Settings

Configure email forwarding seamlessly with the Email Setup feature.
Ensure effective communication and streamline the forwarding of important messages.
Follow the provided steps to set up email server settings and optimize your email workflow.
Tests

The Tests section is designed for applicants to complete assessments as part of the application process.
Administer and manage tests efficiently, review results, and make informed decisions based on applicants' performances.
This feature simplifies the evaluation process and enhances your recruitment procedures.
Profile

Customize your personal profile in the Profile section.
Update your details, change preferences, and tailor MainBoard to suit your needs.
Your profile is your space on MainBoard, so make it uniquely yours.
Installation
To run the TestCompanion web app locally, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/pascallino/TestCompanion.git
Navigate to the project directory:

bash
Copy code
cd TestCompanion
Install dependencies:

More Info
Install and activate venv
To create a Python Virtual Environment, allowing you to install specific dependencies for this python project, we will install venv:

The application was built using python3.8
$ sudo apt-get install python3.8-venv
$ python3 -m venv venv
$ source venv/bin/activate
Install MySQLdb module version 2.0.x
For installing MySQLdb, you need to have MySQL installed: How to install MySQL 8.0 in Ubuntu

$ sudo apt-get install python3-dev
$ sudo apt-get install libmysqlclient-dev
$ sudo apt-get install zlib1g-dev
$ sudo pip3 install mysqlclient

bash
Copy code
pip install -r requirements.txt
Set up the database using the TestCompanion.sql in the current directory:

Update the config.py file with your database configuration.
Run the following commands to create and initialize the database:
bash
Copy code
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
Start the Flask development server:

bash
Copy code
python main.py
Access the web app in your browser at http://100.25.10.60:5001/home

Usage
Once the web app is running, you can access the different features by navigating to the respective sections:

Users: Manage user accounts, roles, and permissions.
Mail Settings: Configure email forwarding and communication settings.
Tests: Administer assessments for applicants and review test results.
Profile: Customize your personal profile and preferences.
Contributing
We welcome contributions to improve and enhance TestCompanion! To contribute:



api endpoints
POST /Addtestuser/<test_id>/<user_id> : Add candidates
GET /rescheduletest/<test_day_id> : Get Reshedule test
POST rescheduletestpost/<test_day_id> Update Test
GET /Timeout/<test_day_id>/<user_id> Timeout page
GET /get_question/<int:question_num>/<test_day_id>/<user_id> Get test questions
GET /get_data/<test_id>/<user_id> Get edited questions
GET /get_test/<user_id> GET test
POST /posttest_getquestions post imported question
GET /editquestion/<test_id>/<user_id> edit question page
POST /authenticate_applicant/<user_id>/<secret_key> verify candidates
GET '/taketest/<user_id>/<key> Get test page
DELETE /question_post_delete delete question 
POST /question_post save questions
POST /uploadimages/<test_id> upload question images
GET /profileboard/<user_id> get profile page
GET /get_profile/<user_id> get user profile
GET /get_company/<user_id> get company data
POST /savecompany/<user_id> save company
POST /saveprofile/<user_id> savwe profile
POST /testmail/<email_id>/<user_id> test mail
GET /get_user/<user_id> get user 
GET /get_mail/<user_id> get mail 
DELETE /deleteuser/<user_id> delete user
POST '/saveuser/<user_id> save user
GET /userboard/<user_id> get user page
GET /mainboard/<user_id> get main dashboard page
GET /Registrationsuccess/<user_id> Registration success page 
POST /signin_post sign in user
POST /computescore/<test_day_id> compute score
GET /testsummary/<test_id>/<test_day_id>/<user_id> summary report
GET /login login page
GET /home
GET /features
GET /contact
GET /signup


