"""empty message

Revision ID: 5a3e0556050b
Revises: 3bbaf0fd21c6
Create Date: 2022-09-16 05:16:52.404133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a3e0556050b'
down_revision = '3bbaf0fd21c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_location', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'location', ['last_location'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'last_location')
    # ### end Alembic commands ###
