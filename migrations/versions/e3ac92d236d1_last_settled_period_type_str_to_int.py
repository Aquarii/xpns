"""last_settled_period type: str to int

Revision ID: e3ac92d236d1
Revises: c457ba6e8bb6
Create Date: 2025-03-24 20:36:25.212669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3ac92d236d1'
down_revision = 'c457ba6e8bb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.alter_column('last_settled_period',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('units', schema=None) as batch_op:
        batch_op.alter_column('last_settled_period',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # ### end Alembic commands ###
