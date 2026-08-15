"""Initial schema creation for shows, seasons, episodes, artworks, and publish_runs

Revision ID: 0001_initial
Revises: 
Create Date: 2026-08-15 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Shows Table
    op.create_table(
        'shows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('section', sa.String(50), nullable=True),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('categories', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_shows_slug', 'shows', ['slug'])
    op.create_index('ix_shows_section', 'shows', ['section'])

    # 2. Seasons Table
    op.create_table(
        'seasons',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('show_id', sa.String(36), sa.ForeignKey('shows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('season_number', sa.Integer(), nullable=False),
    )
    op.create_index('ix_seasons_show_id', 'seasons', ['show_id'])

    # 3. Episodes Table
    op.create_table(
        'episodes',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('season_id', sa.String(36), sa.ForeignKey('seasons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_group', sa.String(255), nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('language', sa.String(10), nullable=False),
        sa.Column('duration_sec', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_episodes_season_id', 'episodes', ['season_id'])
    op.create_index('ix_episodes_content_group', 'episodes', ['content_group'])
    op.create_index('ix_episodes_language', 'episodes', ['language'])
    op.create_index('ix_episodes_status', 'episodes', ['status'])
    op.create_index('ix_episodes_content_group_lang', 'episodes', ['content_group', 'language'])
    op.create_index('ix_episodes_content_group_status', 'episodes', ['content_group', 'status'])

    # 4. Artworks Table
    op.create_table(
        'artworks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('episode_id', sa.String(50), sa.ForeignKey('episodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('file_size_kb', sa.Float(), nullable=True),
        sa.Column('mime_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('episode_id', 'type', name='uq_episode_artwork_type'),
    )
    op.create_index('ix_artworks_episode_id', 'artworks', ['episode_id'])

    # 5. Publish Runs Table
    op.create_table(
        'publish_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('published_by', sa.String(100), nullable=False, server_default='admin@peblo.tv'),
        sa.Column('status', sa.String(20), nullable=False, server_default='success'),
        sa.Column('catalogue_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('shows_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('episodes_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=False, server_default='{}'),
    )
    op.create_index('ix_publish_runs_published_at', 'publish_runs', ['published_at'])
    op.create_index('ix_publish_runs_status', 'publish_runs', ['status'])

def downgrade() -> None:
    op.drop_table('publish_runs')
    op.drop_table('artworks')
    op.drop_table('episodes')
    op.drop_table('seasons')
    op.drop_table('shows')
