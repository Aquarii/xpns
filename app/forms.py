from flask_wtf import FlaskForm
from wtforms import (
    Field,
    StringField,
    SubmitField,
    SelectField,
    DateTimeField,
    TextAreaField,
    IntegerField,
    BooleanField,
    PasswordField,
    ValidationError
)
from wtforms.validators import DataRequired, EqualTo
from app import db
from app.models import User
import sqlalchemy as sa 


class AddBuildingForm(FlaskForm): # needs to set in cookies
    
    name  = StringField('نام ساختمان', validators=[DataRequired()])
    stories_count  = IntegerField('تعداد طبقات')
    units_count  = IntegerField('تعداد واحدها')
    address  = StringField('آدرس')
    cash_reserve  = IntegerField('تراز صندوق')
    description  = TextAreaField('توضیحات')
    submit = SubmitField('تثبیت!')


class AddGroupForm(FlaskForm):
    
    group_name = StringField('نام گروه', validators=[DataRequired()])
    target_building = SelectField('ساختمان')
    members_shares = StringField('تعیین سهم (دستی - پیشرفته)')
    allotting_method = BooleanField('۱. بر حسب نفر', default=False)
    including_vacant_units = BooleanField('۲. حتی شامل واحدهای خالی', default=False)
    reserve = BooleanField('1. صندوق؟', default=False)
    owner = BooleanField('2. مالک واحد (صاحبخانه)',default=False)
    description = TextAreaField('توضیحات')
    submit = SubmitField('تثبیت!')


class AddExpenseForm(FlaskForm):
    
    expense_name = StringField('خرج بابت', validators=[DataRequired()])
    expenditure_amount = IntegerField('مبلغ خرج شده (تومان)', validators=[DataRequired()])
    period = SelectField('دوره')
    target_group = SelectField('گروه پرداخت')
    description = TextAreaField('توضیحات')
    submit = SubmitField('تثبیت!')


class AddUnitForm(FlaskForm):
        
    story = IntegerField('طبقه', validators=[DataRequired()])
    owner = StringField('نام مالک')
    unit_number = IntegerField('شماره واحد')
    building = SelectField('ساختمان')
    resident = StringField('ساکن فعلی')
    balance = IntegerField('تراز بدهی (تومان)', default=0)
    number_of_people = IntegerField('تعداد اعضای خانواده')
    description = TextAreaField('توضیحات')
    submit = SubmitField('تثبیت!')


class AddTransactionForm(FlaskForm):
        
    payer = StringField('پرداخت کننده', validators=[DataRequired()])
    unit_number = SelectField('واحد')
    amount = IntegerField('مبلغ (تومان)', validators=[DataRequired()])
    transaction_date = DateTimeField('تاریخ پرداخت', format="%Y-%m-%d", validators=[DataRequired()])
    description = StringField('توضیحات')
    submit = SubmitField('تثبیت!')


class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    remember_me = BooleanField('مرا به یاد داشته باش.')
    submit = SubmitField('ورود')
    
    
class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    name = StringField('نام و نام خانوادگی')
    email = StringField('ایمیل', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    password2 = PasswordField('تکرار رمز عبور', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('تثبیت!')
    
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == self.username.data))
        if user is not None:
            raise ValidationError('لطفا نام کاربری دیگری انتخاب کنید.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == self.email.data))
        if user is not None:
            raise ValidationError('لطفا از ایمیل دیگری استفاده کنید.')
        

class MgrOptionsForm(FlaskForm):
    personalized_board = BooleanField('بورد خصوصی')
    submit = SubmitField('تثبیت!')
