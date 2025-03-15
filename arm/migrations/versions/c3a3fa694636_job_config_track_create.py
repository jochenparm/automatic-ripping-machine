"""empty message

Revision ID: c3a3fa694636
Revises:
Create Date: 2019-02-09 19:06:50.363700

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c3a3fa694636'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job',
                    sa.Column('job_id', sa.Integer(), nullable=False),
                    sa.Column('arm_version', sa.String(length=20), nullable=True),
                    sa.Column('crc_id', sa.String(length=63), nullable=True),
                    sa.Column('logfile', sa.String(length=256), nullable=True),
                    sa.Column('start_time', sa.DateTime(), nullable=True),
                    sa.Column('stop_time', sa.DateTime(), nullable=True),
                    sa.Column('job_length', sa.String(length=12), nullable=True),
                    sa.Column('status', sa.String(length=32), nullable=True),
                    sa.Column('no_of_titles', sa.Integer(), nullable=True),
                    sa.Column('title', sa.String(length=256), nullable=True),
                    sa.Column('title_auto', sa.String(length=256), nullable=True),
                    sa.Column('title_manual', sa.String(length=256), nullable=True),
                    sa.Column('year', sa.String(length=4), nullable=True),
                    sa.Column('year_auto', sa.String(length=4), nullable=True),
                    sa.Column('year_manual', sa.String(length=4), nullable=True),
                    sa.Column('video_type', sa.String(length=20), nullable=True),
                    sa.Column('video_type_auto', sa.String(length=20), nullable=True),
                    sa.Column('video_type_manual', sa.String(length=20), nullable=True),
                    sa.Column('imdb_id', sa.String(length=15), nullable=True),
                    sa.Column('imdb_id_auto', sa.String(length=15), nullable=True),
                    sa.Column('imdb_id_manual', sa.String(length=15), nullable=True),
                    sa.Column('poster_url', sa.String(length=256), nullable=True),
                    sa.Column('poster_url_auto', sa.String(length=256), nullable=True),
                    sa.Column('poster_url_manual', sa.String(length=256), nullable=True),
                    sa.Column('devpath', sa.String(length=15), nullable=True),
                    sa.Column('mountpoint', sa.String(length=20), nullable=True),
                    sa.Column('hasnicetitle', sa.Boolean(), nullable=True),
                    sa.Column('errors', sa.Text(), nullable=True),
                    sa.Column('disctype', sa.String(length=20), nullable=True),
                    sa.Column('label', sa.String(length=256), nullable=True),
                    sa.Column('ejected', sa.Boolean(), nullable=True),
                    sa.Column('updated', sa.Boolean(), nullable=True),
                    sa.Column('pid', sa.Integer(), nullable=True),
                    sa.Column('pid_hash', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('job_id')
                    )
    op.create_table('config',
                    sa.Column('CONFIG_ID', sa.Integer(), nullable=False),
                    sa.Column('job_id', sa.Integer(), nullable=True),
                    sa.Column('ARM_CHECK_UDF', sa.Boolean(), nullable=True),
                    sa.Column('GET_VIDEO_TITLE', sa.Boolean(), nullable=True),
                    sa.Column('SKIP_TRANSCODE', sa.Boolean(), nullable=True),
                    sa.Column('VIDEOTYPE', sa.String(length=25), nullable=True),
                    sa.Column('MINLENGTH', sa.String(length=6), nullable=True),
                    sa.Column('MAXLENGTH', sa.String(length=6), nullable=True),
                    sa.Column('MANUAL_WAIT', sa.Boolean(), nullable=True),
                    sa.Column('MANUAL_WAIT_TIME', sa.Integer(), nullable=True),
                    sa.Column('ARMPATH', sa.String(length=255), nullable=True),
                    sa.Column('RAWPATH', sa.String(length=255), nullable=True),
                    sa.Column('MEDIA_DIR', sa.String(length=255), nullable=True),
                    sa.Column('EXTRAS_SUB', sa.String(length=255), nullable=True),
                    sa.Column('INSTALLPATH', sa.String(length=255), nullable=True),
                    sa.Column('LOGPATH', sa.String(length=255), nullable=True),
                    sa.Column('LOGLEVEL', sa.String(length=255), nullable=True),
                    sa.Column('LOGLIFE', sa.Integer(), nullable=True),
                    sa.Column('DBFILE', sa.String(length=255), nullable=True),
                    sa.Column('WEBSERVER_IP', sa.String(length=25), nullable=True),
                    sa.Column('WEBSERVER_PORT', sa.Integer(), nullable=True),
                    sa.Column('SET_MEDIA_PERMISSIONS', sa.Boolean(), nullable=True),
                    sa.Column('CHMOD_VALUE', sa.Integer(), nullable=True),
                    sa.Column('SET_MEDIA_OWNER', sa.Boolean(), nullable=True),
                    sa.Column('CHOWN_USER', sa.String(length=50), nullable=True),
                    sa.Column('CHOWN_GROUP', sa.String(length=50), nullable=True),
                    sa.Column('RIPMETHOD', sa.String(length=25), nullable=True),
                    sa.Column('MKV_ARGS', sa.String(length=25), nullable=True),
                    sa.Column('DELRAWFILES', sa.Boolean(), nullable=True),
                    sa.Column('HASHEDKEYS', sa.Boolean(), nullable=True),
                    sa.Column('HB_PRESET_DVD', sa.String(length=256), nullable=True),
                    sa.Column('HB_PRESET_BD', sa.String(length=256), nullable=True),
                    sa.Column('DEST_EXT', sa.String(length=10), nullable=True),
                    sa.Column('HANDBRAKE_CLI', sa.String(length=25), nullable=True),
                    sa.Column('MAINFEATURE', sa.Boolean(), nullable=True),
                    sa.Column('HB_ARGS_DVD', sa.String(length=256), nullable=True),
                    sa.Column('HB_ARGS_BD', sa.String(length=256), nullable=True),
                    sa.Column('EMBY_REFRESH', sa.Boolean(), nullable=True),
                    sa.Column('EMBY_SERVER', sa.String(length=25), nullable=True),
                    sa.Column('EMBY_PORT', sa.String(length=6), nullable=True),
                    sa.Column('EMBY_CLIENT', sa.String(length=25), nullable=True),
                    sa.Column('EMBY_DEVICE', sa.String(length=50), nullable=True),
                    sa.Column('EMBY_DEVICEID', sa.String(length=128), nullable=True),
                    sa.Column('EMBY_USERNAME', sa.String(length=50), nullable=True),
                    sa.Column('EMBY_USERID', sa.String(length=128), nullable=True),
                    sa.Column('EMBY_PASSWORD', sa.String(length=128), nullable=True),
                    sa.Column('EMBY_API_KEY', sa.String(length=64), nullable=True),
                    sa.Column('NOTIFY_RIP', sa.Boolean(), nullable=True),
                    sa.Column('NOTIFY_TRANSCODE', sa.Boolean(), nullable=True),
                    sa.Column('PB_KEY', sa.String(length=64), nullable=True),
                    sa.Column('IFTTT_KEY', sa.String(length=64), nullable=True),
                    sa.Column('IFTTT_EVENT', sa.String(length=25), nullable=True),
                    sa.Column('PO_USER_KEY', sa.String(length=64), nullable=True),
                    sa.Column('PO_APP_KEY', sa.String(length=64), nullable=True),
                    sa.Column('OMDB_API_KEY', sa.String(length=64), nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['job.job_id'], ),
                    sa.PrimaryKeyConstraint('CONFIG_ID')
                    )
    op.create_table('track',
                    sa.Column('track_id', sa.Integer(), nullable=False),
                    sa.Column('job_id', sa.Integer(), nullable=True),
                    sa.Column('track_number', sa.String(length=4), nullable=True),
                    sa.Column('length', sa.Integer(), nullable=True),
                    sa.Column('aspect_ratio', sa.String(length=20), nullable=True),
                    sa.Column('fps', sa.Float(), nullable=True),
                    sa.Column('main_feature', sa.Boolean(), nullable=True),
                    sa.Column('basename', sa.String(length=256), nullable=True),
                    sa.Column('filename', sa.String(length=256), nullable=True),
                    sa.Column('orig_filename', sa.String(length=256), nullable=True),
                    sa.Column('new_filename', sa.String(length=256), nullable=True),
                    sa.Column('ripped', sa.Boolean(), nullable=True),
                    sa.Column('status', sa.String(length=32), nullable=True),
                    sa.Column('error', sa.Text(), nullable=True),
                    sa.Column('source', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['job_id'], ['job.job_id'], ),
                    sa.PrimaryKeyConstraint('track_id')
                    )
    # ### end Alembic commands ###
    # ### commands auto generated by Alembic - please adjust! ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('track')
    op.drop_table('config')
    op.drop_table('job')
    # ### end Alembic commands ###
