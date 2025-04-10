"""Unit.last_settled_period, date to transaction_date

Revision ID: c457ba6e8bb6
Revises: 4d9a60ff94a0
Create Date: 2025-03-23 19:48:17.719153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c457ba6e8bb6'
down_revision = '4d9a60ff94a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column(column_name='date', new_column_name='transaction_date')

    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_settled_period', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.drop_column('last_settled_period')

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column(column_name='transaction_date', new_column_name='date')

    # ### end Alembic commands ###
