"""rename rows on images

Revision ID: 92b8678fbb8f
Revises: 039e63e334d4
Create Date: 2025-01-23 20:55:37.658746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92b8678fbb8f'
down_revision: Union[str, None] = '039e63e334d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('images', sa.Column('caption', sa.String(), nullable=True))
    op.drop_index('ix_images_id', table_name='images')
    op.drop_index('ix_images_name', table_name='images')
    op.drop_column('images', 'url')
    op.drop_column('images', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('images', sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_index('ix_images_name', 'images', ['name'], unique=False)
    op.create_index('ix_images_id', 'images', ['id'], unique=False)
    op.drop_column('images', 'caption')
    op.drop_column('images', 'image_url')
    # ### end Alembic commands ###
