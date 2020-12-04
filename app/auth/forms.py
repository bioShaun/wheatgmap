import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from app.auth.models import User


def legal_username_check(form, field):
    if not re.match("^[0-9a-zA-Z_]+$", field.data):
        raise ValidationError(
            "Only Alphabets, Numbers and Underscore are allowed.")


class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired(),
                    Length(3, 80), legal_username_check])
    email = StringField("Email",
                        validators=[DataRequired(),
                                    Email(),
                                    Length(1, 50)])
    password = PasswordField("Password",
                             validators=[DataRequired(),
                                         Length(6, 50)])
    confirm = PasswordField(
        "Verify Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="password must match")
        ],
    )
    institute = StringField("Institute",
                            validators=[DataRequired(),
                                        Length(1, 80)])
    telephone = StringField("Telephone",
                            validators=[DataRequired(),
                                        Length(1, 20)])
    pub_phone = SelectField('Public Telephone',
                            choices=[(0, "No"), (1, "Yes")],
                            coerce=int)
    photo = StringField('Photo')

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


class EditForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    institute = StringField('Institute', validators=[DataRequired()])
    telephone = StringField('Telephone', validators=[DataRequired()])
    pub_phone = SelectField('Public Telephone',
                            choices=[(0, "No"), (1, "Yes")],
                            coerce=int)
    first_name = StringField('First Name')
    middle_name = StringField('Middle Name')
    family_name = StringField('Family Name')
    photo = StringField('Photo')
    research = TextAreaField('Research Direction')
    profile = TextAreaField('Description')

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.user = None


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

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
