"""Module that handles the forms."""
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, SelectField, FloatField, StringField, PasswordField,
    BooleanField, ValidationError)
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import Required, Length, Email, EqualTo
from .database import User


class ModifyTransactionForm(FlaskForm):
    """Class that instantiates a form for modifying transactions."""

    date = DateTimeLocalField(
        'Date:', format='%Y-%m-%dT%H:%M', validators=[Required()])
    business_name = SelectField('Business Name:', validators=[Required()])
    category_name = SelectField('Category Name:', validators=[Required()])
    account_name = SelectField('Account Name:', validators=[Required()])
    amount = FloatField('Amount:', validators=[Required()])
    modify = SubmitField('Modify')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField(
        'Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    """User registration form."""

    email_validators = [Required(), Length(1, 64), Email()]
    email = StringField('Email', validators=email_validators)
    password_validators = [
        Required(), EqualTo('password2', message='Passwords must match.')]
    password = PasswordField('Password', validators=password_validators)
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """Validate email address."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
