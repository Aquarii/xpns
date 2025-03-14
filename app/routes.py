from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from app import app, db, models, utils
import sqlalchemy as sa
from app.forms import (
    AddExpenseForm,
    AddGroupForm,
    AddBuildingForm,
    AddUnitForm
)
from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/add_building', methods=['GET', 'POST'])
def add_building():
    form = AddBuildingForm()
    if form.validate_on_submit():
        # form data
        name = request.form.get('name')
        stories_count = request.form.get('stories_count', type=int)
        units_count = request.form.get('units_count', type=int)
        address = request.form.get('address')
        description = request.form.get('description')
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
        return redirect(url_for('add_group'))
    return render_template('add_building.html', title='Add Building', form=form)


@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
    stmt = sa.select(models.Building).options(sa.orm.load_only(models.Building.name))
    buildings = db.session.scalars(stmt).all()
    building_names = [(building.building_id, building.name) for building in buildings]
    
    form = AddGroupForm()
    form.building.choices = building_names
    
    if form.validate_on_submit():
        # form data
        group_name = request.form['group_name']
        members_shares = request.form['members_shares']
        building = request.form['building']
        description = request.form['description']
        # write to db
        record = models.Group(
            name=group_name,
            members_shares=members_shares,
            building_id=building,
            description=description
        )
        db.session.add(record)
        db.session.commit()
        
        flash(f'Group {group_name} added.')
        return redirect(url_for('add_expense'))
    return render_template('add_group.html', title='Add Groups', form=form, )


@app.route(rule='/add_expense', methods=['GET', 'POST'])
def add_expense():
    stmt = sa.select(models.Group).options(sa.orm.load_only(models.Group.name))
    groups = db.session.scalars(stmt).all()
    group_choices = [(group.group_id, group.name) for group in groups]

    form = AddExpenseForm()
    form.target_group.choices = group_choices
    form.period.choices = utils.months 
    
    if form.validate_on_submit():
        # form data
        expense_name = request.form.get('expense_name')
        expenditure_amount = request.form.get('expenditure_amount')
        group_id = request.form.get('target_group')
        period = request.form.get('period')
        description = request.form.get('description')
        # write to db
        record = models.Expense(
            name=expense_name,
            amount=expenditure_amount,
            period=period,
            group_id=group_id,
            description= description
        )
        db.session.add(record)
        db.session.commit()

        flash(f'{expenditure_amount} spent for {expense_name}.')
        return redirect(url_for('add_expense'))
    return render_template('add_expense.html', title='Add Expenses', form=form)


@app.route('/add_unit', methods=['GET', 'POST'])
def add_unit():
    stmt = sa.select(models.Building).options(sa.orm.load_only(models.Building.name))
    buildings = db.session.scalars(stmt).all()
    building_names_choices = [(building.building_id, building.name) for building in buildings]

    form = AddUnitForm()
    form.building.choices = building_names_choices

    if form.validate_on_submit():
        # form data
        story = request.form.get('story')
        owner = request.form.get('owner')
        unit_number = request.form.get('unit_number')
        building_id = request.form.get('building')
        resident = request.form.get('resident')
        balance = request.form.get('balance')
        number_of_people = request.form.get('number_of_people')
        description = request.form.get('description')

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


# @app.route('/edit_tables', methods=['GET', 'POST'])
# def edit_tables():
#     buildings = models.Building.query.all()
#     groups = models.Group.query.all()
#     residents = models.Resident.query.all()
#     expenses = models.Expense.query.all()

#     return render_template(
#         'edit_tables.html',
#         title='Edit Tables',
#         buildings=buildings,
#         groups=groups,
#         residents=residents,
#         expenses=expenses
#     )


# @app.route('/remove_building/<int:building_id>')
# def remove_building(building_id):
#     building = models.Building.query.get(building_id)
#     building_name = building.name
#     db.session.delete(building)
#     db.session.commit()

#     flash(f'Deleted {building_name}.')
#     return redirect(url_for('edit_tables'))


# @app.route('/remove_group/<int:group_id>')
# def remove_group(group_id):
#     group = models.Group.query.get(group_id)
#     group_name = group.name
#     db.session.delete(group)
#     db.session.commit()

#     flash(f'Deleted {group_name}.')
#     return redirect(url_for('edit_tables'))
