"""add link uuid field to image post model

Revision ID: d59b86309513
Revises: 271d2a9549ea
Create Date: 2025-01-25 15:43:07.838902

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d59b86309513"
down_revision: Union[str, None] = "271d2a9549ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("image_posts", sa.Column("link_uuid", sa.String(), nullable=True))
    op.alter_column("image_posts", "image_url", existing_type=sa.VARCHAR(), nullable=False)
    op.create_index(op.f("ix_image_posts_link_uuid"), "image_posts", ["link_uuid"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_image_posts_link_uuid"), table_name="image_posts")
    op.alter_column("image_posts", "image_url", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column("image_posts", "link_uuid")
    # ### end Alembic commands ###
