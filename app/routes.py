from typing import Any, Sequence
from functools import reduce
from math import ceil
from urllib.parse import urlsplit
import json
from datetime import datetime, date

from flask_login import login_user, current_user, login_required, logout_user
from flask import flash, redirect, render_template, request, url_for
import sqlalchemy as sa
from app import app, db, utils
from app.forms import (
    AddBuildingForm,
    AddExpenseForm,
    AddGroupForm,
    AddTransactionForm,
    AddUnitForm,
    LoginForm,
    RegistrationForm,
    MgrOptionsForm,
    EditUnitForm,
    PreferencesForm
)
from app.models import (
    Building,
    CashReserve,
    Expense,
    Group,
    Share,
    Transaction,
    Unit,
    User,
    Preferences
)


@app.route("/", methods=["GET", "POST"])
def index():
    select_building = sa.select(Building).join(CashReserve)
    building = db.session.scalar(select_building)

    if building is None:  # first launch
        return redirect(url_for("add_building"))

    building = {
        "id": building.building_id,
        "name": building.name,
        "reserve": building.cash_reserves[0].amount,
    }

    select_residents_balances = sa.select(
        Unit.unit_id,
        Unit.unit_number,
        Unit.resident,
        Unit.balance,
        Unit.owner,
    ).order_by(Unit.unit_number)
    residents_balances = db.session.execute(select_residents_balances).all()
    
    select_period_max = sa.select(sa.func.max(Expense.period))
    period_max = db.session.scalar(select_period_max)
    
    select_expenses_latest = (
        sa.select(Expense)
        .options(sa.orm.load_only(Expense.name, Expense.amount, Expense.period, Expense.description))
        .where(Expense.period == period_max)
        .order_by(Expense.expense_id.desc())
    )
    expenses = db.session.scalars(select_expenses_latest).all()
    print(period_max)
    
    prefs = db.session.scalar(sa.select(Preferences))
    include_latest = prefs.include_latest_expenses_in_print if prefs else False

    context = {
        "title": "تابلوی اعلانات",
        "expenses_list": expenses,
        "building": building,
        "residents_balances": residents_balances,
        "period_max": period_max,
        "ceil": ceil,
        "include_latest_expenses_in_print": include_latest
    }
    return render_template("index.html", **context)


@app.route("/expenses")
def view_expenses():
    # Query params (GET)
    q = request.args.get("q", type=str)                   # search in name/description
    period = request.args.get("period", type=int)         # exact match
    min_amount = request.args.get("min_amount", type=int) # >=
    max_amount = request.args.get("max_amount", type=int) # <=

    filters = []

    if q:
        like = f"%{q}%"
        filters.append(sa.or_(Expense.name.ilike(like),
                              Expense.description.ilike(like)))
    if period is not None:
        filters.append(Expense.period == period)
    if min_amount is not None:
        filters.append(Expense.amount >= min_amount)
    if max_amount is not None:
        filters.append(Expense.amount <= max_amount)

    stmt = (
        sa.select(Expense)
        .options(
            sa.orm.load_only(
                Expense.expense_id,
                Expense.name,
                Expense.amount,
                Expense.period,
                Expense.description,
            )
        )
        .order_by(Expense.expense_id.desc())
    )

    if filters:
        stmt = stmt.where(sa.and_(*filters))

    expenses = db.session.scalars(stmt).all()

    return render_template(
        "view_expenses.html",
        expenses=expenses,
        title="همه مخارج",
        q=q or "",
        period=period or "",
        min_amount="" if min_amount is None else min_amount,
        max_amount="" if max_amount is None else max_amount,
    )


@app.route("/add_building", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
            members_shares = json.loads(
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
@login_required
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

        flash(f"{expenditure_amount} تومان برای {expense_name} ثبت شد.")
        return redirect(url_for("add_expense"))
    else:
        print("Form Not Validated")
    return render_template("add_expense.html", title="Add Expenses", form=form)


@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    
    unit_id = request.args.get("unit_id", type=int)
    payer = request.args.get("payer")
    amount = request.args.get("amount", type=int)
    date_q = request.args.get("date")  # if 'today', we’ll set today below

    stmt = sa.select(Unit)
    units = db.session.scalars(stmt).all()
    unit_names_choices = [(unit.unit_id, unit.unit_number) for unit in units]
    form = AddTransactionForm(request.form)
    form.unit_number.choices = unit_names_choices

    if unit_id:
        form.unit_number.data = unit_id  # FIXME -
    if payer:
        form.payer.data = payer
    if amount is not None:
        form.amount.data = amount  # FIXME -

    # Always set to today's date when date=today OR when no date provided
    if date_q == "today" or date_q is None:
        # Use a naive datetime that matches wtforms format "%Y-%m-%d"
        today_dt = datetime.combine(date.today(), datetime.min.time())
        form.transaction_date.data = today_dt
    
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
            # getting reserve amount from paid shares[]
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
            reserved_cash.amount += reduce(lambda x, y: x + y, reserve_amount, 0)
        db.session.commit()

        flash(f"تراکنش واحد {unit_id} ثبت شد.")
        return redirect(url_for("add_transaction"))
    else:
        print("Form Not Validated!")
    return render_template("add_transaction.html", title="Add Transaction", form=form)


@app.route(rule="/details/<unit_id>")
def view_details(unit_id):
    select_unpaid_shares = (
        sa.select(Share.amount, Expense.name, Expense.period)
        .join(Expense)
        .where(~Share.paid)
        .where(Share.unit_id == unit_id)
    )
    unit_unpaid_shares = db.session.execute(select_unpaid_shares).all()
    current_debt = (
        db.session.scalar(
            sa.select(sa.func.sum(Share.amount))
            .group_by(Share.unit_id)
            .having(~Share.paid)
            .where(Share.unit_id == unit_id)
        )
        or 0
    )
    unit = db.session.get(Unit, unit_id)
    unit_balance = unit.balance
    prev_debt = unit_balance - current_debt

    context = {
        "shares": unit_unpaid_shares,
        "title": f"Unit {unit.unit_number}'s share details ({unit.resident})",
        "prev_debt": prev_debt,
        "ceil": ceil,
    }
    return render_template("view_details.html", **context)


@app.route("/view_units")
def view_units():
    select_units = (
        sa.select(Unit)
        .options(
            sa.orm.load_only(
                Unit.unit_id,
                Unit.unit_number,
                Unit.resident,
                Unit.owner,
                Unit.balance,
                Unit.number_of_people,
            )
        )
        .order_by(Unit.unit_number)
    )
    units = db.session.scalars(select_units).all()

    return render_template("view_units.html", units=units, title="Units")


@app.route("/login", methods=["GET", "POST"])
def login():
    # if current_user.is_authenticated:
    #     return  redirect(url_for("index"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        print(user)
        if user is None or not user.check_password(form.password.data):
            flash("نام کاربری یا رمز عبور نامعتبر است.", category="error")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, email=form.email.data, name=form.name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("تبریک! کاربر جدید افزوده شد.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/mgr_options", methods=["GET", "POST"])
def mgr_options():
    form = MgrOptionsForm(request.form)
    return render_template("mgr_options.html", form=form, title="Options")


@app.route("/edit_unit", methods=["GET", "POST"])
@login_required
def edit_unit():
    form = EditUnitForm(request.form)

    # populate dropdown
    units = db.session.scalars(sa.select(Unit)).all()
    form.unit_id.choices = [
        (u.unit_id, f"واحد {u.unit_number} - {u.resident}") for u in units
    ]

    # read preselected id from querystring
    selected_id = request.args.get("unit_id", type=int)

    # prefill on GET (or when we have a selected id)
    if request.method == "GET":
        if selected_id:
            unit = db.session.get(Unit, selected_id)
            if unit:
                form.unit_id.data = unit.unit_id
                form.resident.data = unit.resident
                form.owner.data = unit.owner
                form.balance.data = unit.balance
                form.number_of_people.data = unit.number_of_people
                form.description.data = unit.description

        return render_template("edit_unit.html", title="ویرایش واحد", form=form)

    # handle POST (update)
    if form.validate_on_submit():
        unit = db.session.get(Unit, form.unit_id.data)
        if not unit:
            flash("واحد یافت نشد!", "error")
            return redirect(url_for("edit_unit"))

        unit.resident = form.resident.data
        unit.owner = form.owner.data
        unit.balance = form.balance.data
        unit.number_of_people = form.number_of_people.data
        unit.description = form.description.data
        db.session.commit()

        flash(f"واحد {unit.unit_number} با موفقیت به‌روزرسانی شد.", "success")
        # redirect back to list, or stay here:
        return redirect(url_for("view_units"))

    return render_template("edit_unit.html", title="ویرایش واحد", form=form)


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    # ensure singleton exists
    prefs = db.session.scalar(sa.select(Preferences)) 
    if prefs is None:
        prefs = Preferences()
        db.session.add(prefs)
        db.session.commit()
    
    form = PreferencesForm(obj=prefs)

    form = PreferencesForm(request.form, 
        include_latest_expenses_in_print=prefs.include_latest_expenses_in_print
    )

    if form.validate_on_submit():
        prefs.include_latest_expenses_in_print = form.include_latest_expenses_in_print.data
        form.populate_obj(prefs)
        db.session.commit()
        flash('تنظیمات ذخیره شد.', 'success')
        return redirect(url_for('preferences'))

    return render_template("preferences.html", title="تنظیمات مدیر", form=form)
