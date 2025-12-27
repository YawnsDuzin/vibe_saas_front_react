"""add post_files table

Revision ID: 8c2e4f1a9b3d
Revises: 5a7b563ec14e
Create Date: 2025-12-27 14:57:24.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c2e4f1a9b3d'
down_revision: Union[str, None] = '5a7b563ec14e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """업그레이드 마이그레이션 - post_files 테이블 생성"""
    op.create_table(
        'post_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0, comment='표시 순서'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'file_id', name='uq_post_file')
    )
    op.create_index(op.f('ix_post_files_id'), 'post_files', ['id'], unique=False)


def downgrade() -> None:
    """다운그레이드 마이그레이션 - post_files 테이블 삭제"""
    op.drop_index(op.f('ix_post_files_id'), table_name='post_files')
    op.drop_table('post_files')
