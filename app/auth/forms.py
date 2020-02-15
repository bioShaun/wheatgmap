from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from app.auth.models import User


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    institute = StringField('Institute',
                            validators=[DataRequired()])
    telephone = StringField('Telephone',
                            validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm = PasswordField('Verify Password',
                            validators=[DataRequired(), EqualTo('password',
                                                                message='password must match')])

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if self.user:
            self.username.errors.append('Username already registered')
            return False
        self.user = User.query.filter_by(email=self.email.data).first()
        if self.user:
            self.email.errors.append('Email already registerd')
            return False
        return True


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.user = User.query.filter_by(email=self.username.data).first()
            if not self.user:
                self.username.errors.append('User/Email not register')
                return False

        if not self.user.verify_password(self.password.data):
            self.password.errors.append('Password Error')
            return False

        if not self.user.is_active:
            self.username.errors.append('User not active')
            return False

        return True
