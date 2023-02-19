"""removing text column from tablelogs

Revision ID: 6778b2e66fb9
Revises: 642ab64a3e8d
Create Date: 2023-01-17 11:46:15.533532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6778b2e66fb9'
down_revision = '642ab64a3e8d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TableLogs', 'text')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TableLogs', sa.Column('text', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
