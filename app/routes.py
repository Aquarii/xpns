from typing import Any, Sequence
from functools import reduce
from math import ceil

import pandas as pd
import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from app import app, db, utils
from app.forms import (
    AddBuildingForm,
    AddExpenseForm,
    AddGroupForm,
    AddTransactionForm,
    AddUnitForm,
)
from app.models import Building, CashReserve, Expense, Group, Share, Transaction, Unit




@app.route("/", methods=["GET", "POST"])
def index():
    select_residents_balance = sa.select(
        Unit.unit_number, Unit.resident, Unit.balance, Unit.owner
    ).order_by(Unit.unit_number)
    results = db.session.execute(select_residents_balance).all()

    select_building = sa.select(Building).join(CashReserve)
    building = db.session.scalar(select_building)
    building = {
        "id": building.building_id,
        "name": building.name,
        "reserve": building.cash_reserves[0].amount,
    }
    
    select_expenses = sa.select(Expense).options(sa.orm.load_only(Expense.name, Expense.amount))
    expenses = db.session.scalars(select_expenses).all()
    print(expenses)  

    context = {
        "title": "Shares",
        "expenses_list": expenses,
        "building": building,
        "results": results,
        "ceil": ceil
    }
    return render_template("index.html", **context)


@app.route("/add_building", methods=["GET", "POST"])
def add_building():
    form = AddBuildingForm(request.form)
    if form.validate_on_submit():
        # form data
        name = form.name.data
        stories_count = form.stories_count.data
        units_count = form.units_count.data
        address = form.address.data
        cash_reserve = form.cash_reserve.data or 0
        description = form.description.data
        # save form data to db
        building = Building(
            name=name,
            stories_count=stories_count,
            units_count=units_count,
            address=address,
            description=description,
        )
        db.session.add(building)
        db.session.commit()
        reserve = CashReserve(
            name="صندوق روز مبادا",
            building_id=building.building_id,
            amount=cash_reserve,
        )
        db.session.add(reserve)
        db.session.commit()

        flash(f"{name} ایجاد شد.")
        return redirect(url_for("add_unit"))
    return render_template("add_building.html", title="Add Building", form=form)


@app.route("/add_unit", methods=["GET", "POST"])
def add_unit():
    stmt = sa.select(Building).options(sa.orm.load_only(Building.name))
    buildings = db.session.scalars(stmt).all()
    building_names_choices = [
        (building.building_id, building.name) for building in buildings
    ]

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
            resident=resident,
            balance=balance,
            number_of_people=number_of_people,
            description=description,
        )
        print(record)
        db.session.add(record)
        db.session.commit()

        flash(f"واحد {unit_number} ذخیره شد.")
        return redirect(url_for("add_unit"))
    return render_template("add_unit.html", title="Add Units", form=form)


@app.route("/add_group", methods=["GET", "POST"])
def add_group():
    form = AddGroupForm(request.form)

    # populate Building field
    select_buildings = sa.select(Building).options(sa.orm.load_only(Building.name))
    buildings = db.session.scalars(select_buildings).all()
    building_choices = [(building.building_id, building.name) for building in buildings]
    form.target_building.choices = building_choices

    def calculate_member_share_percent(
        allotting_to_persons: bool, including_vacant_units: bool
    ):
        select_units = sa.select(Unit).column(Unit.number_of_people)
        units = db.session.scalars(select_units).all()
        members_shares = {unit.unit_id: 0 for unit in units}

        if allotting_to_persons:  # occupied units implied.
            denominator = sum(unit.number_of_people for unit in units)
            for unit in units:
                members_shares[unit.unit_id] = (
                    round(100 / denominator, 2) * unit.number_of_people
                )

        elif not allotting_to_persons and not including_vacant_units:
            denominator = sum(True for unit in units if unit.number_of_people != 0)
            for unit in units:
                if unit.number_of_people != 0:
                    members_shares[unit.unit_id] = round(100 / denominator, 2)

        else:
            denominator = len(units)
            members_shares = {
                unit.unit_id: round(100 / denominator, 2) for unit in units
            }

        return members_shares

    if form.validate_on_submit():
        # getting form data
        group_name = form.group_name.data
        building_id = form.target_building.data
        owner = form.owner.data
        reserve = form.reserve.data
        members_shares = form.members_shares.data if form.members_shares.data else None
        if not members_shares:
            allotting_to_people = form.allotting_method.data
            including_vacant_units = form.including_vacant_units.data
            members_shares = calculate_member_share_percent(
                allotting_to_people, including_vacant_units
            )
        else:
            members_shares = (
                members_shares
                if members_shares.startswith("{") and members_shares.endswith("}")
                else "".join(["{", members_shares, "}"])
            )
        description = form.description.data

        # write form data to db
        record = Group(
            name=group_name,
            owner=owner,
            reserve=reserve,
            building_id=building_id,
            members_shares=members_shares,
            description=description,
        )
        db.session.add(record)
        db.session.commit()

        flash(f" گروه «{group_name}» اضافه شد.")
        return redirect(url_for("add_expense"))
    return render_template("add_group.html", title="Add Groups", form=form)


@app.route(rule="/add_expense", methods=["GET", "POST"])
def add_expense():

    select_groups = sa.select(Group).options(
        sa.orm.load_only(Group.name, Group.members_shares)
    )
    groups: Sequence[Group] = db.session.scalars(select_groups).all()
    group_choices = [(group.group_id, group.name) for group in groups]

    form = AddExpenseForm(request.form)
    form.target_group.choices = group_choices
    form.period.choices = utils.months

    if form.validate_on_submit():
        # form data
        expense_name = form.expense_name.data
        expenditure_amount = form.expenditure_amount.data
        period = form.period.data
        group_id = form.target_group.data
        description = form.description.data

        # write Expenses to db
        expense_record = Expense(
            name=expense_name,
            amount=expenditure_amount,
            period=period,
            group_id=group_id,
            description=description,
        )
        print(expense_record)
        db.session.add(expense_record)
        db.session.commit()

        # Allot to units in "Shares" table and update units balances
        select_group = select_groups.where(Group.group_id == group_id)
        group = db.session.scalar(select_group)
        for unit_id in group.members_shares.keys():
            share_amount = expenditure_amount * group.members_shares[unit_id] / 100
            unit_share = Share(
                unit_id=unit_id,
                amount=share_amount,
                expense_id=expense_record.expense_id,
            )
            db.session.add(unit_share)
            unit = db.session.get(Unit, unit_id)
            unit.balance += share_amount
            db.session.commit()

        flash(f"{expenditure_amount} ریال برای {expense_name} ثبت شد.")
        return redirect(url_for("add_expense"))
    else:
        print("Form Not Validated")
    return render_template("add_expense.html", title="Add Expenses", form=form)


@app.route("/add_transaction", methods=["GET", "POST"])
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
            transaction_date=transaction_date,
            description=description,
        )
        db.session.add(record)

        # make the unit's debt paid
        unit = db.session.get(Unit, unit_id)
        unit.balance -= amount
        if unit.balance <= 0:
            db.session.execute(
                sa.update(Share)
                .where(Share.unit_id == unit_id)
                .values(paid=True)
                .returning(Share.unit_id, Share.paid)
            )
            # getting reserve amount from paid shares
            # ? until resident pays his full debt (balance <= 0),
            # ? the reserve amount wont get add to cash-reserve
            # ? but as soon as he pays in the folowing months,
            # ? all the previous reserve debts gets added to the cash-reserves
            select_reserve_amount = (
                sa.select(Share.amount)
                .join(Expense)
                .join(Group)
                .where(Share.unit_id == unit_id)
                .where(Share.paid)
                .where(Group.reserve)
            )
            reserve_amount = db.session.scalars(select_reserve_amount).all()

            reserved_cash = db.session.get(CashReserve, 1)
            reserved_cash.amount = reduce(lambda x, y: x + y, reserve_amount)
            print(reserved_cash.amount)
        db.session.commit()

        flash(f"تراکنش واحد {unit_id} ثبت شد.")
        return redirect(url_for("add_transaction"))
    else:
        print("Form Not Validated!")
    return render_template("add_transaction.html", title="Add Transaction", form=form)


@app.route(rule="/balance_sheet")
def view_balance_sheet():
    pass
