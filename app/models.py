from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Numeric, JSON, UniqueConstraint
from typing import List, Optional
from datetime import datetime, timezone
from app import db 

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
    __tablename__ = 'buildings'
    
    # Columns
    building_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(30))
    stories_count: Mapped[int]
    units_count: Mapped[int]
    address: Mapped[Optional[str]] = mapped_column(String(256), deferred=True)
    description: Mapped[Optional[str]] = mapped_column(String(256), deferred=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    # Relationships
    units: Mapped[list["Unit"]] = relationship(back_populates='building', cascade='all, delete-orphan', init=False)
    groups: Mapped[list["Group"]] = relationship(back_populates='building', cascade='all, delete-orphan', init=False)
    __table_args__ = (UniqueConstraint(name, address, name='building_unique_const'),)
    
    # def __repr__(self) -> str:
    #     return f'Building object: name: {self.name}, Id: {self.id}'


class Group(db.Model):
    __tablename__ = 'groups'
    
    # Columns
    group_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(64))
    members_shares: Mapped[Optional[list[str]]] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    # Foreign Key
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey(Building.building_id, ondelete='CASCADE', onupdate='CASCADE')) # ForeignKey
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(back_populates='group', init=False)
    building: Mapped["Building"] = relationship(back_populates='groups', init=False)


class Expense(db.Model):
    __tablename__ = 'expenses'

    # Columns
    expense_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(64))
    amount: Mapped[int] = mapped_column(Numeric)
    period: Mapped[int]
    description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    # Foreign Key
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey(Group.group_id, ondelete='CASCADE', onupdate='CASCADE')) # ForeignKey
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    # Relationships
    group: Mapped["Group"] = relationship(back_populates='expenses', init=False)

    # def __repr__(self):
    #     return f'Expense object: name: {self.name}, amount: {self.amount}'


class Unit(db.Model):
    __tablename__ = 'units'

    # Columns
    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    unit_number: Mapped[int] = mapped_column(Integer)
    resident: Mapped[str]
    number_of_people: Mapped[int]
    story: Mapped[int]
    owner: Mapped[str]
    balance: Mapped[int]
    description: Mapped[Optional[str]]
    # ForeignKey
    building_id: Mapped[int] = mapped_column(
        ForeignKey(Building.building_id, ondelete="CASCADE", onupdate="CASCADE"),
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    building: Mapped["Building"] = relationship(back_populates='units', init=False)

    __table_args__ = (UniqueConstraint(unit_number, building_id, name='unit_number_building_unique_const'),)


class Share(db.Model):
    __table_name__ = 'shares'
    
    # Columns
    share_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    period: Mapped[int]
    unit_number: Mapped[int]
    amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))


class Transaction(db.Model):
    __table_name__ = 'transactions'
    
    # Columns
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    sender: Mapped[str] = mapped_column(index=True)
    amount: Mapped[int]
    date: Mapped[Optional[str]] 
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))


#######################################################################################
##                                 FOR LATER VERSIONS                                 ##
#######################################################################################

# class Resident(db.Model):
#     __tablename__ = 'residents'

#     # Columns
#     resident_id: Mapped[int] = mapped_column(primary_key=True, init=False)
#     name: Mapped[str] = mapped_column(String(30))
#     body_count: Mapped[int] = mapped_column(Integer)
#     phone_number: Mapped[str] = mapped_column(String(13))
#     residency_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
#     # residency_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, init=False)
#     unit_id: Mapped[int] = mapped_column(Integer, ForeignKey(Unit.unit_id, ondelete='CASCADE', onupdate='CASCADE')) # ForeignKey
#     description: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
#     is_manager: Mapped[bool] = mapped_column(Boolean, default=False)

#     # Relationships
#     unit: Mapped['Unit'] = relationship(back_populates='resident', init=False)

#     __table_args__ = (UniqueConstraint(phone_number, name='phone_number_unique_const'), UniqueConstraint(unit_id, name='unit_unique_const'))

#     # def __repr__(self) -> str:
#     #     return f'Object: {self.name}, has a family of {self.body_count}'
