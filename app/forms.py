from wtforms import (
    Field,
    StringField,
    SubmitField,
    SelectField,
    DateTimeField,
    TextAreaField,
    IntegerField,
    BooleanField
)
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
from flask_wtf import FlaskForm
from datetime import date
from app import app, db, utils
from app.models import Group, Building, Expense, Unit
import sqlalchemy as sa


class AddBuildingForm(FlaskForm): # needs to set in cookies
    
    name  = StringField('Building Name', validators=[DataRequired()])
    stories_count  = IntegerField('Number of Stories')
    units_count  = IntegerField('Units Count')
    address  = StringField('Address')
    description  = TextAreaField('Description')
    submit = SubmitField('Submit')


class AddGroupForm(FlaskForm):
    
    group_name = StringField('Group Name', validators=[DataRequired()])
    members_shares = StringField('Members Shares', validators=[DataRequired()])
    owner = BooleanField('Expense for owner?', default=False)
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


class AddExpenseForm(FlaskForm):
    
    expense_name = StringField('Expense Name', validators=[DataRequired()])
    expenditure_amount = IntegerField('Expenditure Amount (Tomans)', validators=[DataRequired()])
    target_group = SelectField('Payers')
    period = SelectField('Period')
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


class AddUnitForm(FlaskForm):
        
    story = IntegerField('Story', validators=[DataRequired()])
    owner = StringField('Owner')
    unit_number = IntegerField('Unit Number')
    building = SelectField('Building')
    resident = StringField('Resident Name')
    balance = IntegerField('Balance')
    number_of_people = IntegerField('Number of family members')
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


class AddTransactionForm(FlaskForm):
        
    payer = StringField('Payer')
    unit_number = SelectField('Unit Number')
    amount = IntegerField('Amount (Toman)')
    transaction_date = DateTimeField('Date', format="%Y-%m-%d")
    description = StringField('توضیحات')
    submit = SubmitField('Submit')