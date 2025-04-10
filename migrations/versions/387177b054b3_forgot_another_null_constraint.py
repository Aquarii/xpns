"""forgot ANOTHER NULL constraint!

Revision ID: 387177b054b3
Revises: 5ded6ff114c7
Create Date: 2025-03-30 17:25:56.834179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '387177b054b3'
down_revision = '5ded6ff114c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cash_reserves', schema=None) as batch_op:
        batch_op.drop_constraint('fk_cash_reserves_building_id_buildings', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_cash_reserves_building_id_buildings'), 'buildings', ['building_id'], ['building_id'], onupdate='CASCADE', ondelete='NO ACTION')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cash_reserves', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_cash_reserves_building_id_buildings'), type_='foreignkey')
        batch_op.create_foreign_key('fk_cash_reserves_building_id_buildings', 'buildings', ['building_id'], ['building_id'], onupdate='CASCADE', ondelete='SET NULL')

    # ### end Alembic commands ###
