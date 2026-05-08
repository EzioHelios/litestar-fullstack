"""add protocol to dataapp_monitorequipment

Revision ID: a1b2c3d4e5f6
Revises: 73fe10facb3e
Create Date: 2026-03-06

参考 PRD 4.1：Device 表增加 protocol 字段，用于区分采集策略 (MQTT / modbus / http_yunji)。
"""
import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "73fe10facb3e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dataapp_monitorequipment",
        sa.Column("protocol", sa.String(20), nullable=True, server_default="http_yunji"),
    )


def downgrade() -> None:
    op.drop_column("dataapp_monitorequipment", "protocol")
