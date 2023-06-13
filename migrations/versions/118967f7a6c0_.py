"""empty message

Revision ID: 118967f7a6c0
Revises: 1c152ad587f5
Create Date: 2022-10-20 15:32:25.992497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '118967f7a6c0'
down_revision = '1c152ad587f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likes', sa.Column('created_date', sa.DateTime(), nullable=False))
    op.drop_column('likes', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likes', sa.Column('date', sa.DATETIME(), nullable=False))
    op.drop_column('likes', 'created_date')
    # ### end Alembic commands ###