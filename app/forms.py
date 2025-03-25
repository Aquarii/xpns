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
    RadioField
)
from wtforms.validators import DataRequired


class AddBuildingForm(FlaskForm): # needs to set in cookies
    
    name  = StringField('نام ساختمان', validators=[DataRequired()])
    stories_count  = IntegerField('تعداد طبقات')
    units_count  = IntegerField('تعداد واحدها')
    address  = StringField('آدرس')
    description  = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddGroupForm(FlaskForm):
    
    group_name = StringField('نام گروه', validators=[DataRequired()])
    members_shares = StringField('تعیین سهم (دستی - پیشرفته)', validators=[DataRequired()])
    owner = RadioField('سهم الخرج برای', choices=[(0,'مستأجر'), (1,'مالک')], default=0)
    allotting_method = RadioField('تخصیص بر اساس', choices=[(0,'تعداد واحدها'), (1,'تعداد نفرات')], default=0)
    occupied_units_only = RadioField('شمولیت', choices=[(1,'فقط واحدهای پُر'), (0,'تمام واحدها')], default=1)
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddExpenseForm(FlaskForm):
    
    expense_name = StringField('خرج بابت', validators=[DataRequired()])
    expenditure_amount = IntegerField('مبلغ خرج شده (ریال)', validators=[DataRequired()])
    owner = RadioField('سهم الخرج برای', choices=[(0,'مستأجر'), (1,'مالک')], default=0)
    allotting_method = RadioField('تخصیص بر اساس', choices=[(0,'تعداد واحدها'), (1,'تعداد نفرات')], default=0)
    occupied_units_only = RadioField('شمولیت', choices=[(1,'فقط واحدهای پُر'), (0,'تمام واحدها')], default=1)
    target_group = SelectField('گروه پرداخت')
    period = SelectField('دوره')
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddUnitForm(FlaskForm):
        
    story = IntegerField('طبقه', validators=[DataRequired()])
    owner = StringField('نام مالک')
    unit_number = IntegerField('شماره واحد')
    building = SelectField('ساختمان')
    resident = StringField('ساکن فعلی')
    balance = IntegerField('تراز بدهی (ریال)', default=0)
    number_of_people = IntegerField('تعداد اعضای خانواده')
    description = TextAreaField('توضیحات')
    submit = SubmitField('ثبت کردن')


class AddTransactionForm(FlaskForm):
        
    payer = StringField('پرداخت کننده')
    unit_number = SelectField('واحد')
    amount = IntegerField('مبلغ (ریال)')
    transaction_date = DateTimeField('تاریخ پرداخت', format="%Y-%m-%d")
    description = StringField('توضیحات')
    submit = SubmitField('ثبت کردن')


class DashboardForm(FlaskForm):
    
    period = SelectField('برج')
    submit = SubmitField('ثبت کردن')