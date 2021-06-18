#import for all flask form related objects: pip install flask-wtf
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField ,PasswordField ,SubmitField ,BooleanField ,TextAreaField
from wtforms.validators import DataRequired, Length ,Email ,EqualTo ,ValidationError
from Main.models import User

class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=10)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password= PasswordField('Password',validators=[DataRequired()])
    confirm_password= PasswordField("Confirm Password",validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user =User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username Already exits!,Please try different one.')

    def validate_email(self, email):
        user =User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exits!,Please try different one.')

class AccountUpdateForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=10)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    picture=FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user =User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username Already exits!,Please try different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user =User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exits!,Please try different one.')


class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=10)])
    password= PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content= TextAreaField('Content',validators=[DataRequired()])
    submit=SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):
        user =User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email, you must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')