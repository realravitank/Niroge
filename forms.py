from flask_wtf import FlaskForm
from flask import session
from wtforms import StringField, PasswordField, SelectField, FloatField, RadioField, IntegerField, DateField
from wtforms.fields.html5 import DateField
from datetime import datetime, date, timedelta
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange

class AddUserForm(FlaskForm):

    """Form for adding users."""

    goal = SelectField('Goal', choices = [('lose','Lose Weight'), ('maintain','Maintain Weight'), ('gain', 'Gain Weight')], validators=[DataRequired()])
    activity = SelectField('Daily Average Activity Level', choices = [('sedentary', 'Sedentary'), ('lightly active', 'Lightly Active'), ('active', 'Active')], validators=[DataRequired()])
    year = IntegerField('Year', default = 2004, validators=[DataRequired(), NumberRange(min=1850, max=2004, message='Invalid year input')])
    month = IntegerField('Month', default = 12, validators=[DataRequired(), NumberRange(min=1, max=12, message='Invalid month input')])
    day = IntegerField('Day', default = 31, validators=[DataRequired(), NumberRange(min=1, max=31, message='Invalid date input')])

    unit = SelectField('Units', choices = [('imp', 'Imperial (lbs/inch)'), ('met', 'Metric (kg/cm)')], validators=[DataRequired()])

    weight = FloatField('Current Weight', validators=[DataRequired()])
    goal_weight = FloatField('Goal Weight', validators=[DataRequired()])
    rate = SelectField('Progress Speed', choices = [('fast', 'Fast'), ('normal', 'Normal'), ('slow', 'Slow')], validators=[DataRequired()])

    height = FloatField('Height', validators=[DataRequired()])
    diet_type = RadioField('Diet Restrictions', choices = [('vegan', 'Vegan'), ('veg', 'Vegetarian'), ('gf', 'Gluten Free')], validators=[Optional()])
    budget = FloatField('Monthly Budget', validators=[Optional()]) 


class EditUserForm(FlaskForm):

    """Form for editing users."""
    
    email = StringField('E-mail', validators=[DataRequired(), Email()]) 
    goal = SelectField('Goal', choices = [('lose','Lose Weight'), ('maintain','Maintain Weight'), ('gain', 'Gain Weight')], validators=[DataRequired()])
    activity = SelectField('Daily Average Activity Level', choices = [('sedentary', 'Sedentary'), ('light', 'Lightly Active'), ('active', 'Active')], validators=[DataRequired()])
    unit = SelectField('Units', choices = [('imp', 'Imperial (lbs)'), ('met', 'Metric (kg)')], validators=[DataRequired()])

    weight = FloatField('Current Weight', validators=[DataRequired()])
    goal_weight = FloatField('Goal Weight', validators=[DataRequired()])

    rate = SelectField('Progress Speed', choices = [('fast', 'Fast'), ('normal', 'Normal'), ('slow', 'Slow')], validators=[DataRequired()])

    diet_type = RadioField('Diet Restrictions', choices = [('vegan', 'Vegan'), ('veg', 'Vegetarian'), ('gf', 'Gluten Free')], validators=[Optional()])
    budget = FloatField('Monthly Budget', validators=[Optional()]) 
    

class LoginForm(FlaskForm):

    """Form to login users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6), DataRequired()])

class SignUpForm(FlaskForm):

    """Form to signup users."""
    name = StringField('Full Name', validators=[DataRequired()])
    sex = SelectField('Sex', choices = [('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])

    email = StringField('E-mail', validators=[DataRequired(), Email()])

    password = PasswordField('New Password (at least 6 charecters)', validators=[Length(min=6), DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')


class EditUserWeightForm(FlaskForm):

    """Form for editing weight."""
    unit = SelectField('Units', choices = [('imp', 'Imperial (lbs)'), ('met', 'Metric (kg)')], validators=[DataRequired()])
    weight = FloatField('New Weight', validators=[DataRequired()])


class AddMealForm(FlaskForm):

    """Form to search meals."""

    meal = StringField('')