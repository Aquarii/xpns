from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from app import app, db, models, utils
import sqlalchemy as sa
from app.forms import (
    AddExpenseForm,
    AddGroupForm,
    AddBuildingForm,
    AddUnitForm,
    AddTransactionForm
)
from datetime import datetime
import json


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


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
        record = models.Building(
            name=name,
            stories_count=stories_count,
            units_count=units_count,
            address=address,
            description=description
        )
        db.session.add(record)
        db.session.commit()
        
        flash(f'Building {name} added.')
        return redirect(url_for('add_unit'))
    return render_template('add_building.html', title='Add Building', form=form)


@app.route('/add_unit', methods=['GET', 'POST'])
def add_unit():
    stmt = sa.select(models.Building).options(sa.orm.load_only(models.Building.name))
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
        record = models.Unit(
            story=story,
            owner=owner,
            unit_number=unit_number,
            building_id=building_id,
            resident = resident,
            balance = balance,
            number_of_people = number_of_people,
            description=description,
            # occupied=occupied
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
        members_shares = form.members_shares.data
        owner = form.owner.data
        description = form.description.data
        # write to db
        record = models.Group(
            name=group_name,
            members_shares=members_shares,
            owner=owner,
            description=description,
        )
        db.session.add(record)
        db.session.commit()

        flash(f'Group {group_name} added.')
        return redirect(url_for('add_expense'))    
    return render_template('add_group.html', title='Add Groups', form=form)


@app.route(rule='/add_expense', methods=['GET', 'POST'])
def add_expense():
    stmt = sa.select(models.Group).options(
        sa.orm.load_only(models.Group.name, models.Group.members_shares)
    )
    groups = db.session.scalars(stmt).all()
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
        expense_record = models.Expense(
            name=expense_name,
            amount=expenditure_amount,
            period=period,
            group_id=group_id,
            description= description
        )
        db.session.add(expense_record)
        db.session.commit()

        # Calculate and populate Shares table
        stmt = sa.select(models.Group).where(models.Group.group_id == group_id)
        group = db.session.scalar(stmt)
        for item in eval(group.members_shares).items():
            unit_share = models.Share(
                period=period,
                unit_number=item[0],
                amount=item[1] * int(expenditure_amount),
                expense=expense_name,
            )
            print(unit_share)
            db.session.add(unit_share)
            db.session.commit()

        flash(f'{expenditure_amount} spent for {expense_name}.')
        return redirect(url_for('add_expense'))
    return render_template('add_expense.html', title='Add Expenses', form=form)


@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    stmt = sa.select(models.Unit)
    units = db.session.scalars(stmt).all()
    unit_names_choices = [(unit.unit_id, unit.unit_number) for unit in units]

    form = AddTransactionForm(request.form)
    form.unit_number.choices = unit_names_choices

    if form.validate_on_submit():
        # form data
        payer = form.payer.data
        unit_number = form.unit_number.data
        amount = form.amount.data
        transaction_date = form.transaction_date.data
        description = form.description.data

        # write to db
        record = models.Unit(
            payer=payer,
            unit_number=unit_number,
            amount=amount,
            transaction_date = transaction_date,
            description=description,
        )
        print(record)
        db.session.add(record)
        db.session.commit()
        
        flash(f'تراکنش واحد {unit_number} ثبت شد.')
        return redirect(url_for('add_transaction'))
    return render_template('add_transaction.html', title='Add Transaction', form=form)
