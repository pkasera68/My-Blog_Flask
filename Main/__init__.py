import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
#SQLAlchemy is a Python SQL Toolkit and Object Relational Mapper
#that gives application developers the full power and flexibility of using SQL.
from flask_bcrypt import Bcrypt #to encode user passwords, becuse we are
# storing their unique hash values in the database after encoding them.
from flask_login import LoginManager
#LoginManager class handles user logins and also handles sessions in the background for us.
app = Flask(__name__)

#for using the forms securely we are setting the secret key ,
# A secret key will protect against the modifying cookies, cross site request forgery attacks, etc.
app.config['SECRET_KEY'] = "e8f50a95048a25e9dd7dfd59452a90e4"
#to get a random secret key ,here
#on the cmd we have used following commands
#python (to open python interpreter)
#import secrets
#secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager =LoginManager(app)
#setting login view so that if user tries to access account page without login ,then login_required opens this
#login_view.
login_manager.login_view='login'
login_manager.login_message_category='info'

#setting necessary constants like MAIL_SERVER,MAIL_PORT and whether to use TLS or not, to send mail.
# here we are using mail server of gmail.
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
#for sending any mail to the user we also need a email server so
#setting the username and password for the email server with which we want to send mails to the user.
# here below we are setting the username and pass in environment var and then send them for security.
#check corey schafer's video on environment variables.
app.config['MAIL_USERNAME']=os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD']=os.environ.get('EMAIL_PASS')
mail = Mail(app)
from Main import routes