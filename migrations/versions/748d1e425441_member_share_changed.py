"""member share changed.

Revision ID: 748d1e425441
Revises: d0ded2d44fe1
Create Date: 2025-03-16 17:42:48.341712

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '748d1e425441'
down_revision = 'd0ded2d44fe1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.alter_column('members_shares',
               existing_type=sqlite.JSON(),
               type_=sa.String(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.alter_column('members_shares',
               existing_type=sa.String(),
               type_=sqlite.JSON(),
               existing_nullable=False)

    # ### end Alembic commands ###
