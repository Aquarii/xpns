from flask_wtf import FlaskForm
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
from wtforms.validators import DataRequired


class AddBuildingForm(FlaskForm): # needs to set in cookies
    
    name  = StringField('نام ساختمان', validators=[DataRequired()])
    stories_count  = IntegerField('تعداد طبقات')
    units_count  = IntegerField('تعداد واحدها')
    address  = StringField('آدرس')
    cash_reserve  = IntegerField('تراز صندوق')
    description  = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddGroupForm(FlaskForm):
    
    group_name = StringField('نام گروه', validators=[DataRequired()])
    target_building = SelectField('ساختمان')
    members_shares = StringField('تعیین سهم (دستی - پیشرفته)')
    allotting_method = BooleanField('۱. بر حسب نفر', default=False)
    including_vacant_units = BooleanField('۲. حتی شامل واحدهای خالی', default=False)
    reserve = BooleanField('1. صندوق؟', default=False)
    owner = BooleanField('2. مالک واحد (صاحبخانه)',default=False)
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddExpenseForm(FlaskForm):
    
    expense_name = StringField('خرج بابت', validators=[DataRequired()])
    expenditure_amount = IntegerField('مبلغ خرج شده (تومان)', validators=[DataRequired()])
    period = SelectField('دوره')
    target_group = SelectField('گروه پرداخت')
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddUnitForm(FlaskForm):
        
    story = IntegerField('طبقه', validators=[DataRequired()])
    owner = StringField('نام مالک')
    unit_number = IntegerField('شماره واحد')
    building = SelectField('ساختمان')
    resident = StringField('ساکن فعلی')
    balance = IntegerField('تراز بدهی (تومان)', default=0)
    number_of_people = IntegerField('تعداد اعضای خانواده')
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddTransactionForm(FlaskForm):
        
    payer = StringField('پرداخت کننده')
    unit_number = SelectField('واحد')
    amount = IntegerField('مبلغ (تومان)')
    transaction_date = DateTimeField('تاریخ پرداخت', format="%Y-%m-%d")
    description = StringField('توضیحات')
    submit = SubmitField('ثبت کردن')

