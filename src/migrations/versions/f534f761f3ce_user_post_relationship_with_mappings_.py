"""user-post relationship with mappings fix typo for model

Revision ID: f534f761f3ce
Revises: f4f90ed04a89
Create Date: 2025-01-24 20:37:08.705627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f534f761f3ce'
down_revision: Union[str, None] = 'f4f90ed04a89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
