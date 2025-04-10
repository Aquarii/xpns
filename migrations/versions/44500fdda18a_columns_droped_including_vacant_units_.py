"""columns droped: including_vacant_units, allotting_method! back to where I was!

Revision ID: 44500fdda18a
Revises: 0d4902a47e00
Create Date: 2025-03-29 01:02:56.823104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44500fdda18a'
down_revision = '0d4902a47e00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_column('including_vacant_units')
        batch_op.drop_column('allotting_to_people')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.add_column(sa.Column('allotting_to_people', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('including_vacant_units', sa.BOOLEAN(), nullable=True))

    # ### end Alembic commands ###
