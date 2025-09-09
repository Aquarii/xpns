import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from flask_login import UserMixin
from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

#######################################################################################
##                                     IMPORTANT                                      ##
##   ANNOTATED DECLARATIVE TYPINGS ARE NOT CONSISTENT! SOME MAPPED_COLUMN TYPES ARE   ##
##                      EXCESSIVE AND SHOULD BE CLEANED/REMOVED,                      ##
##         SOME DELIBERATELY DIFFER FROM MAPPED (PYTHON TYPES) AND SHOULDN'T.         ##
#######################################################################################

# pk_int = Annotated[int, mapped_column(primary_key=True, init=False)]

# class TimestampMixin:
#     created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))


class Building(db.Model):
    __tablename__ = "buildings"

    # Columns
    building_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(30))
    stories_count: Mapped[int]
    units_count: Mapped[int]
    address: Mapped[str | None] = mapped_column(String(256), deferred=True)
    description: Mapped[str | None] = mapped_column(String(256), deferred=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    units: Mapped[List["Unit"]] = relationship(
        back_populates="building", cascade="all, delete-orphan", init=False
    )
    cash_reserves: Mapped[List["CashReserve"]] = relationship(
        back_populates="building", init=False
    )
    groups: Mapped[List["Group"]] = relationship(
        back_populates="building", cascade="all, delete-orphan", init=False
    )

    # Constraints
    __table_args__ = (UniqueConstraint(name, address, name="building_unique_const"),)

    def __repr__(self) -> str:
        return f"Building: {self.name}, id: {self.building_id}"


class Unit(db.Model):
    __tablename__ = "units"

    # Columns
    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    unit_number: Mapped[int] = mapped_column(Integer)
    resident: Mapped[str]
    number_of_people: Mapped[int]
    story: Mapped[int]
    owner: Mapped[str]
    balance: Mapped[int]
    description: Mapped[str | None]
    building_id: Mapped[int] = mapped_column(
        ForeignKey(Building.building_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    building: Mapped["Building"] = relationship(back_populates="units", init=False)
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="unit", init=False
    )
    shares: Mapped[List["Share"]] = relationship(back_populates="unit", init=False)
    # resident: Mapped["Resident"] = relationship(back_populates="unit", init=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            unit_number, building_id, name="unit_number_building_unique_const"
        ),
    )

    def __repr__(self):
        return f"Unit __repr__: unit number: {self.unit_number}, resident: {self.resident}, family of {self.number_of_people}, debt: {self.balance}"


class Transaction(db.Model):
    __tablename__ = "transactions"

    # Columns
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    payer: Mapped[str] = mapped_column(index=True)
    amount: Mapped[int]
    transaction_date: Mapped[datetime | None]
    description: Mapped[str | None]
    unit_id: Mapped[int] = mapped_column(
        ForeignKey(Unit.unit_id, ondelete="CASCADE", onupdate="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    unit: Mapped["Unit"] = relationship(back_populates="transactions", init=False)

    def __repr__(self):
        return f"Transaction __repr__: payer: {self.payer}, amount: {self.amount}"


class Group(db.Model):
    __tablename__ = "groups"

    # Columns
    group_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(64))
    members_shares: Mapped[Dict | None] = mapped_column(JSON)
    description: Mapped[str | None] = mapped_column(String)
    building_id: Mapped[int] = mapped_column(
        ForeignKey(Building.building_id, ondelete="CASCADE", onupdate="CASCADE")
    )
    owner: Mapped[bool] = mapped_column(default=0)
    reserve: Mapped[bool] = mapped_column(default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc).astimezone()
    )

    # Relationships
    building: Mapped["Building"] = relationship(back_populates="groups", init=False)
    expenses: Mapped["Expense"] = relationship(back_populates='group', init=False)

    def __repr__(self):
        return f"Group __repr__: name: {self.name}, shares: {self.members_shares}"


class Expense(db.Model):
    __tablename__ = "expenses"

    # Columns
    expense_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(64))
    amount: Mapped[int]
    period: Mapped[int]
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey(Group.group_id, onupdate="CASCADE", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    shares: Mapped[List["Share"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan", init=False
    )
    group: Mapped["Group"] = relationship(back_populates='expenses', init=False) 

    def __repr__(self):
        return f"Expense __repr__: name: {self.name}, amount: {self.amount}"


class Share(db.Model):
    __tablename__ = "shares"

    # Columns
    share_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    amount: Mapped[int]
    expense_id: Mapped[int] = mapped_column(
        ForeignKey(Expense.expense_id, ondelete="CASCADE", onupdate="CASCADE")
    )
    unit_id: Mapped[int] = mapped_column(
        ForeignKey(Unit.unit_id, ondelete="CASCADE", onupdate="CASCADE")
    )
    paid: Mapped[bool] = mapped_column(default=False, index=True, init=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )

    # Relationships
    expense: Mapped["Expense"] = relationship(back_populates="shares", init=False)
    unit: Mapped["Unit"] = relationship(back_populates="shares", init=False)

    def __repr__(self):
        return f"Share __repr__: unit: {self.unit.unit_number}, amount: {self.amount}"


class CashReserve(db.Model):
    __tablename__ = "cash_reserves"

    reserve_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    building_id: Mapped[int] = mapped_column(
        ForeignKey(Building.building_id, onupdate="CASCADE", ondelete="NO ACTION")
    )
    amount: Mapped[int] = mapped_column(default=0)

    # Relationships
    building: Mapped["Building"] = relationship(
        back_populates="cash_reserves", init=False
    )


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Columns
    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default_factory=uuid.uuid4, init=False)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str]
    password_hash: Mapped[Optional[str]] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.user_id

@login.user_loader 
def load_user(user_id):
    return db.session.get(User, user_id)


#######################################################################################
##^                                 FOR LATER VERSIONS                                 ##
#######################################################################################
# class Resident(db.Model, UserMixin):
#     __tablename__ = 'residents'
# 
# # Columns
# resident_id: Mapped[int] = mapped_column(primary_key=True, init=False)
# name: Mapped[str] = mapped_column(String(30))
# body_count: Mapped[int] = mapped_column(Integer)
# phone_number: Mapped[str] = mapped_column(String(13))
# residency_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
# # residency_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, init=False)
# unit_id: Mapped[int] = mapped_column(Integer, ForeignKey(Unit.unit_id, ondelete='CASCADE', onupdate='CASCADE')) # ForeignKey
# description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
# is_manager: Mapped[bool] = mapped_column(Boolean, default=False)

# # Relationships
# unit: Mapped['Unit'] = relationship(back_populates='resident', init=False)
# __table_args__ = (UniqueConstraint(phone_number, name='phone_number_unique_const'), UniqueConstraint(unit_id, name='unit_unique_const'))

# def __repr__(self) -> str:
#     return f'__repr__: {self.name}, has a family of {self.body_count}'
