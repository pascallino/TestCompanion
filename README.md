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
Access the web app in your browser at http://localhost:5000.

Usage
Once the web app is running, you can access the different features by navigating to the respective sections:

Users: Manage user accounts, roles, and permissions.
Mail Settings: Configure email forwarding and communication settings.
Tests: Administer assessments for applicants and review test results.
Profile: Customize your personal profile and preferences.
Contributing
We welcome contributions to improve and enhance TestCompanion! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-improvement).
Make your changes and commit them (git commit -am 'Add new feature').
Push to the branch (git push origin feature-improvement).
Create a new Pull Request.
Support
For any issues or questions related to TestCompanion, please submit a new issue.

