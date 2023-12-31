"""empty message

Revision ID: c206deef6fc8
Revises: a753654c4f71
Create Date: 2022-08-30 00:55:47.912838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c206deef6fc8'
down_revision = 'a753654c4f71'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('registered_on', sa.DateTime(), nullable=False))
    op.add_column('user', sa.Column('confirmed', sa.Boolean(), nullable=False))
    op.add_column('user', sa.Column('confirmed_on', sa.DateTime(), nullable=True))
    op.create_unique_constraint(None, 'user', ['username'])
    op.drop_column('user', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.VARCHAR(length=1000), nullable=True))
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'confirmed_on')
    op.drop_column('user', 'confirmed')
    op.drop_column('user', 'registered_on')
    # ### end Alembic commands ###
