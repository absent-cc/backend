"""first rev

Revision ID: be2a5fc73aaa
Revises: 
Create Date: 2022-01-19 16:44:13.918182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be2a5fc73aaa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teachers',
    sa.Column('tid', sa.String(length=16), nullable=False),
    sa.Column('first', sa.String(length=255), nullable=True),
    sa.Column('last', sa.String(length=255), nullable=True),
    sa.Column('school', sa.String(length=4), nullable=True),
    sa.PrimaryKeyConstraint('tid')
    )
    op.create_table('users',
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('gid', sa.String(length=255), nullable=True),
    sa.Column('first', sa.String(length=255), nullable=True),
    sa.Column('last', sa.String(length=255), nullable=True),
    sa.Column('school', sa.String(length=4), nullable=True),
    sa.Column('grade', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('gid')
    )
    op.create_table('absences',
    sa.Column('tid', sa.String(length=16), nullable=False),
    sa.Column('note', sa.String(length=255), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=False),
    sa.ForeignKeyConstraint(['tid'], ['teachers.tid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tid', 'date')
    )
    op.create_table('classes',
    sa.Column('tid', sa.String(length=16), nullable=False),
    sa.Column('block', sa.String(length=8), nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['tid'], ['teachers.tid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['uid'], ['users.uid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('tid', 'block', 'uid')
    )
    op.create_table('sessions',
    sa.Column('sid', sa.String(length=16), nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=False),
    sa.Column('last_accessed', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['users.uid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('sid', 'uid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    op.drop_table('classes')
    op.drop_table('absences')
    op.drop_table('users')
    op.drop_table('teachers')
    # ### end Alembic commands ###