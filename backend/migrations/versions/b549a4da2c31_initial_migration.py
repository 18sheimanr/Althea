"""Initial migration

Revision ID: b549a4da2c31
Revises: 
Create Date: 2024-06-29 19:35:21.778336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b549a4da2c31'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patient_username'), 'patient', ['username'], unique=True)
    op.create_table('provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('specialty', sa.String(length=255), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('preferred_contact', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('insurance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_name', sa.String(length=255), nullable=True),
    sa.Column('policy_number', sa.String(length=255), nullable=True),
    sa.Column('coverage_start_date', sa.Date(), nullable=True),
    sa.Column('coverage_end_date', sa.Date(), nullable=True),
    sa.Column('deductible', sa.Float(), nullable=True),
    sa.Column('copay', sa.Float(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient_provider',
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['provider_id'], ['provider.id'], ),
    sa.PrimaryKeyConstraint('patient_id', 'provider_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('patient_provider')
    op.drop_table('insurance')
    op.drop_table('provider')
    op.drop_index(op.f('ix_patient_username'), table_name='patient')
    op.drop_table('patient')
    # ### end Alembic commands ###
