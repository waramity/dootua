"""empty message

Revision ID: a753654c4f71
Revises: e277a9b3fa33
Create Date: 2022-08-30 00:51:57.253299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a753654c4f71'
down_revision = 'e277a9b3fa33'
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
