"""AKB+Device

Revision ID: e5e275310997
Revises: 
Create Date: 2024-07-29 02:10:52.649285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5e275310997'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('akb',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('device',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('akb_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['akb_id'], ['akb.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device')
    op.drop_table('akb')
    # ### end Alembic commands ###
