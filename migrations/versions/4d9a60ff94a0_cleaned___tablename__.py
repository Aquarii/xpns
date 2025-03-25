"""cleaned: __tablename__!

Revision ID: 4d9a60ff94a0
Revises: c410dc9b9e1b
Create Date: 2025-03-22 13:01:26.442632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d9a60ff94a0'
down_revision = 'c410dc9b9e1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shares',
    sa.Column('share_id', sa.Integer(), nullable=False),
    sa.Column('period', sa.Integer(), nullable=False),
    sa.Column('unit_number', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('expense_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['expense_id'], ['expenses.expense_id'], name=op.f('fk_shares_expense_id_expenses'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('share_id', name=op.f('pk_shares'))
    )
    with op.batch_alter_table('shares', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_shares_period'), ['period'], unique=False)
        batch_op.create_index(batch_op.f('ix_shares_unit_number'), ['unit_number'], unique=False)

    op.create_table('transactions',
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('payer', sa.String(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['unit_id'], ['units.unit_id'], name=op.f('fk_transactions_unit_id_units'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('transaction_id', name=op.f('pk_transactions'))
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_payer'), ['payer'], unique=False)

    with op.batch_alter_table('share', schema=None) as batch_op:
        batch_op.drop_index('ix_share_period')
        batch_op.drop_index('ix_share_unit_number')

    op.drop_table('share')
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_index('ix_transaction_payer')

    op.drop_table('transaction')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('transaction_id', sa.INTEGER(), nullable=False),
    sa.Column('amount', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATETIME(), nullable=True),
    sa.Column('unit_id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('payer', sa.VARCHAR(), nullable=False),
    sa.ForeignKeyConstraint(['unit_id'], ['units.unit_id'], name='fk_transaction_unit_id_units', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('transaction_id', name='pk_transaction')
    )
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.create_index('ix_transaction_payer', ['payer'], unique=False)

    op.create_table('share',
    sa.Column('share_id', sa.INTEGER(), nullable=False),
    sa.Column('period', sa.INTEGER(), nullable=False),
    sa.Column('unit_number', sa.INTEGER(), nullable=False),
    sa.Column('amount', sa.INTEGER(), nullable=False),
    sa.Column('expense_id', sa.INTEGER(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.ForeignKeyConstraint(['expense_id'], ['expenses.expense_id'], name='fk_share_expense_id_expenses', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('share_id', name='pk_share')
    )
    with op.batch_alter_table('share', schema=None) as batch_op:
        batch_op.create_index('ix_share_unit_number', ['unit_number'], unique=False)
        batch_op.create_index('ix_share_period', ['period'], unique=False)

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_payer'))

    op.drop_table('transactions')
    with op.batch_alter_table('shares', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_shares_unit_number'))
        batch_op.drop_index(batch_op.f('ix_shares_period'))

    op.drop_table('shares')
    # ### end Alembic commands ###
