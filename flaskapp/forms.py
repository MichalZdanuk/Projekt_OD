from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskapp.models import User
import flaskapp.validate_data as validator


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password'), Length(min=2, max=50)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        if not validator.is_userfield_valid(username.data):
            raise ValidationError('Invalid username syntax')
    
    def validate_password(self, password):
        if not validator.is_userfield_valid(password.data):
            raise ValidationError('Invalid password syntax')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_password(self, password):
        if not validator.is_userfield_valid(password.data):
            raise ValidationError('Invalid password syntax')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email(), Length(min=2, max=50)])
    old_password = PasswordField('Old_Password', validators=[DataRequired(), Length(min=2, max=50)])                    
    new_password = PasswordField('Password')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
            if not validator.is_userfield_valid(username.data):
                raise ValidationError('Invalid username syntax')

    def validate_old_password(self, old_password):
        if not validator.is_userfield_valid(old_password.data):
            raise ValidationError('Invalid password syntax')

    def validate_new_password(self, new_password):
        if new_password.data != "":
            if not validator.is_userfield_valid(new_password.data):
                raise ValidationError('Invalid password syntax')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class UploadPictureForm(FlaskForm):
    public_picture = FileField('Upload Public Picture', validators=[FileAllowed(['png'])])
    protected_picture = FileField('Upload Protected Picture', validators=[FileAllowed(['png'])])
    submit = SubmitField('Update')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email(), Length(min=2, max=50)])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password'), Length(min=2, max=50)])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        if not validator.is_userfield_valid(password.data):
            raise ValidationError('Invalid password syntax')
    def validate_confirm_password(self, confirm_password):
        if not validator.is_userfield_valid(confirm_password.data):
            raise ValidationError('Invalid password syntax')

class PermissionForm(FlaskForm):
    allowed_user = StringField('Allow User')
    disallowed_user = StringField('Disallow User')
    submit = SubmitField('Manage Permission')