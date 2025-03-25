from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from app import app, db, utils
from app.models import Building, Unit, Group, Expense, Share, Transaction
import sqlalchemy as sa
from app.forms import (
    AddExpenseForm,
    AddGroupForm,
    AddBuildingForm,
    AddUnitForm,
    AddTransactionForm,
    DashboardForm
)
import pandas as pd


@app.route('/', methods=['GET','POST'])
def index():
    ''' #! Not yet generalized! 
    
    debts = db.session.query(
        Share.unit_number, sa.func.sum(Share.amount)
    ).group_by(Share.unit_number).all()
    print(debts)
    
    for unit_number, amount in debts:
        unit = (
            db.session.query(Unit)
            .where(Unit.unit_number == unit_number)
            .first()
        )
        print(unit.unit_number,unit.balance)
        unit.balance += amount
        print(unit.unit_number, unit.balance)
        # db.session.add(unit)
        # db.session.commit()
        #! '''
        
    results = (
        db.session.query(
            Unit.unit_number, 
            Unit.resident, 
            Unit.balance
        ).order_by(Unit.unit_number)
    ).all()
    results_df = pd.DataFrame(results).set_index('unit_number')

    context = {
        'title': 'Results',
        'results': results_df,
    }
    return render_template('index.html', **context)


@app.route('/add_building', methods=['GET', 'POST'])
def add_building():
    form = AddBuildingForm(request.form)
    if form.validate_on_submit():
        # form data
        name = form.name.data
        stories_count = form.stories_count.data
        units_count = form.units_count.data
        address = form.address.data
        description = form.description.data
        # save form data to db
        record = Building(
            name=name,
            stories_count=stories_count,
            units_count=units_count,
            address=address,
            description=description
        )
        db.session.add(record)
        db.session.commit()
        
        flash(f'بلوک {name} ایجاد شد.')
        return redirect(url_for('add_unit'))
    return render_template('add_building.html', title='Add Building', form=form)


@app.route('/add_unit', methods=['GET', 'POST'])
def add_unit():
    stmt = sa.select(Building).options(sa.orm.load_only(Building.name))
    buildings = db.session.scalars(stmt).all()
    building_names_choices = [(building.building_id, building.name) for building in buildings]

    form = AddUnitForm(request.form)
    form.building.choices = building_names_choices

    if form.validate_on_submit():
        # form data
        story = form.story.data 
        owner = form.owner.data 
        unit_number = form.unit_number.data 
        building_id = form.building.data 
        resident = form.resident.data 
        balance = form.balance.data 
        number_of_people = form.number_of_people.data 
        description = form.description.data 

        # write to db
        record = Unit(
            story=story,
            owner=owner,
            unit_number=unit_number,
            building_id=building_id,
            resident = resident,
            balance = balance,
            number_of_people = number_of_people,
            description=description,
        )
        print(record)
        db.session.add(record)
        db.session.commit()
        
        flash(f'واحد {unit_number} ذخیره شد.')
        return redirect(url_for('add_unit'))
    return render_template('add_unit.html', title='Add Units', form=form)


@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
    form = AddGroupForm(request.form)

    if form.validate_on_submit():
        # form data
        group_name = form.group_name.data
        owner = bool(eval(form.owner.data))
        members_shares = (
            form.members_shares.data
            if form.members_shares.data.startswith("{")
            and form.members_shares.data.endswith("}")
            else "".join(["{", form.members_shares.data, "}"])
        )
        description = form.description.data
        # write to db
        record = Group(
            name=group_name,
            members_shares=members_shares,
            owner=owner,
            description=description,
        )
        db.session.add(record)
        db.session.commit()

        flash(f' گروه {group_name} اضافه شد.')
        return redirect(url_for('add_expense'))    
    return render_template('add_group.html', title='Add Groups', form=form)


@app.route(rule='/add_expense', methods=['GET', 'POST'])
def add_expense():
    select_groups = sa.select(Group).options(
        sa.orm.load_only(Group.name, Group.members_shares)
    )
    groups = db.session.scalars(select_groups).all()
    group_choices = [(group.group_id, group.name) for group in groups]

    form = AddExpenseForm(request.form)
    form.target_group.choices = group_choices
    form.period.choices = utils.months 

    if form.validate_on_submit():
        # form data
        expense_name = form.expense_name.data
        expenditure_amount = form.expenditure_amount.data
        group_id = form.target_group.data
        period = form.period.data
        description = form.description.data

        # write expenses to db
        expense_record = Expense(
            name=expense_name,
            amount=expenditure_amount,
            period=period,
            group_id=group_id,
            description= description
        )
        db.session.add(expense_record)
        db.session.commit()

        # Calculate and populate Shares table
        select_group = select_groups.where(Group.group_id == group_id)
        group = db.session.scalar(select_group)
        for item in eval(group.members_shares).items():
            unit_share = Share(
                period=period,
                unit_id=item[0],
                amount=item[1] * int(expenditure_amount),
                expense_id=expense_record.expense_id
            )
            db.session.add(unit_share)
            db.session.commit()
        
        # Calculating and Writing Unit Balance in db
        select_unit_total_debt = (
            sa.select(
                Unit.unit_id,
                sa.func.sum(Share.amount).label('balance'),
            )
            .join(Share)
            .join(Expense)
            .group_by(Unit.unit_id)
            .having(Expense.period > Unit.last_settled_period)
        )
        total_debts = db.session.execute(select_unit_total_debt).all()
        
        for debt in total_debts:
            unit = db.session.get(Unit, debt[0])
            unit.balance += debt[1]
            # db.session.add(unit)
            db.session.commit()
        
        flash(f'{expenditure_amount} ریال برای {expense_name} ثبت شد.')
        return redirect(url_for('add_expense'))
    return render_template('add_expense.html', title='Add Expenses', form=form)


@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    stmt = sa.select(Unit)
    units = db.session.scalars(stmt).all()
    unit_names_choices = [(unit.unit_id, unit.unit_number) for unit in units]

    form = AddTransactionForm(request.form)
    form.unit_number.choices = unit_names_choices

    if form.validate_on_submit():
        # form data 
        payer = form.payer.data
        unit_id = form.unit_number.data
        amount = form.amount.data
        transaction_date = form.transaction_date.data
        description = form.description.data

        # write form data to db
        record = Transaction(
            payer=payer,
            unit_id=unit_id,
            amount=amount,
            transaction_date = transaction_date,
            description=description,
        )
        db.session.add(record)
        db.session.commit()
        
        # Subtract from respective unit's balance and update it in db
        select_last_period = sa.select(sa.func.max(Expense.period))
        last_period = db.session.scalar(select_last_period)
        unit = db.session.get(Unit, unit_id)
        unit.balance -= amount * 10000
        if unit.balance <= 0:
            unit.last_settled_period = last_period
        db.session.commit()
        
        flash(f'تراکنش واحد {unit_id} ثبت شد.')
        return redirect(url_for('add_transaction'))
    return render_template('add_transaction.html', title='Add Transaction', form=form)


@app.route(rule='/balance_sheet')
def view_balance_sheet():
    pass
