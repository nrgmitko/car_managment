"""Initial migration

Revision ID: 598595015372
Revises: 
Create Date: 2024-12-25 17:52:51.666807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '598595015372'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tables
    op.create_table('car',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('brand', sa.String(length=255), nullable=False),
                    sa.Column('model', sa.String(length=255), nullable=False),
                    sa.Column('year', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('carservice',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('city', sa.String(length=255), nullable=False),
                    sa.Column('capacity', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('carservicelink',
                    sa.Column('car_id', sa.Integer(), nullable=False),
                    sa.Column('service_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['car_id'], ['car.id']),
                    sa.ForeignKeyConstraint(['service_id'], ['carservice.id']),
                    sa.PrimaryKeyConstraint('car_id', 'service_id')
                    )

    op.create_table('maintenancerequest',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('service_id', sa.Integer(), nullable=False),
                    sa.Column('car_id', sa.Integer(), nullable=False),
                    sa.Column('date', sa.Date(), nullable=False),
                    sa.Column('status', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['car_id'], ['car.id']),
                    sa.ForeignKeyConstraint(['service_id'], ['carservice.id']),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Drop old tables
    op.drop_index('ix_maintenances_car_id', table_name='maintenances')
    op.drop_index('ix_maintenances_garage_id', table_name='maintenances')
    op.drop_index('ix_maintenances_id', table_name='maintenances')
    op.drop_index('ix_maintenances_scheduled_date', table_name='maintenances')
    op.drop_index('ix_maintenances_service_type', table_name='maintenances')
    op.drop_table('maintenances')
    op.drop_index('ix_garages_id', table_name='garages')
    op.drop_table('garages')


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('garages',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('capacity', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_garages_id', 'garages', ['id'], unique=False)
    op.create_table('maintenances',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('car_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('garage_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('service_type', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('scheduled_date', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_maintenances_service_type', 'maintenances', ['service_type'], unique=False)
    op.create_index('ix_maintenances_scheduled_date', 'maintenances', ['scheduled_date'], unique=False)
    op.create_index('ix_maintenances_id', 'maintenances', ['id'], unique=False)
    op.create_index('ix_maintenances_garage_id', 'maintenances', ['garage_id'], unique=False)
    op.create_index('ix_maintenances_car_id', 'maintenances', ['car_id'], unique=False)
    op.drop_table('maintenancerequest')
    op.drop_table('carservicelink')
    op.drop_table('carservice')
    op.drop_table('car')
    # ### end Alembic commands ###
