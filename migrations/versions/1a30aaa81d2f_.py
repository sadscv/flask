"""empty message

Revision ID: 1a30aaa81d2f
Revises: b4dc62d76aed
Create Date: 2016-12-12 16:00:23.634265

"""

# revision identifiers, used by Alembic.
revision = '1a30aaa81d2f'
down_revision = 'b4dc62d76aed'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Posts', sa.Column('title', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Posts', 'title')
    ### end Alembic commands ###
