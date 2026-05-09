"""add carbon factor asset library

Revision ID: b7c9d2e4f6a8
Revises: a1b2c3d4e5f6
Create Date: 2026-05-08
"""

import sqlalchemy as sa
from alembic import op

revision = "b7c9d2e4f6a8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def _id_column() -> sa.Column:
    return sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False)


def _audit_columns() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def upgrade() -> None:
    op.add_column("dataapp_emissionfactor", sa.Column("source_system", sa.String(length=64), nullable=True))
    op.add_column("dataapp_emissionfactor", sa.Column("source_snapshot_id", sa.String(length=64), nullable=True))
    op.add_column("dataapp_emissionfactor", sa.Column("raw_record_id", sa.BigInteger(), nullable=True))
    op.add_column("dataapp_emissionfactor", sa.Column("projection_status", sa.String(length=24), nullable=True))
    op.add_column("dataapp_emissionfactor", sa.Column("review_status", sa.String(length=24), nullable=True))

    op.create_table(
        "carbon_factor_import_batch",
        _id_column(),
        sa.Column("snapshot_id", sa.String(length=64), nullable=False),
        sa.Column("package_name", sa.String(length=255), nullable=True),
        sa.Column("package_version", sa.String(length=32), nullable=True),
        sa.Column("package_type", sa.String(length=64), nullable=True),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.String(length=512), nullable=True),
        sa.Column("built_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_started_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_finished_at", sa.DateTime(), nullable=True),
        sa.Column("is_complete", sa.Boolean(), nullable=False),
        sa.Column("checksum_verified", sa.Boolean(), nullable=False),
        sa.Column("import_status", sa.String(length=24), nullable=False),
        sa.Column("library_count", sa.Integer(), nullable=False),
        sa.Column("category_count", sa.Integer(), nullable=False),
        sa.Column("leaf_category_count", sa.Integer(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("detail_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("xlsx_count", sa.Integer(), nullable=False),
        sa.Column("manifest_payload", sa.JSON(), nullable=True),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carbon_factor_import_batch")),
        sa.UniqueConstraint("source_system", "snapshot_id", name="uq_carbon_factor_batch_source_snapshot"),
    )
    op.create_index(op.f("ix_carbon_factor_import_batch_snapshot_id"), "carbon_factor_import_batch", ["snapshot_id"])
    op.create_index(
        op.f("ix_carbon_factor_import_batch_source_system"),
        "carbon_factor_import_batch",
        ["source_system"],
    )

    op.create_table(
        "carbon_factor_library",
        _id_column(),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("library_year", sa.String(length=16), nullable=False),
        sa.Column("library_code", sa.String(length=32), nullable=False),
        sa.Column("library_name", sa.String(length=255), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("source_pkid", sa.String(length=64), nullable=True),
        sa.Column("source_year_id", sa.String(length=64), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carbon_factor_library")),
        sa.UniqueConstraint(
            "source_system",
            "library_year",
            "library_code",
            name="uq_carbon_factor_library_source_year_code",
        ),
    )
    op.create_index(op.f("ix_carbon_factor_library_library_code"), "carbon_factor_library", ["library_code"])
    op.create_index(op.f("ix_carbon_factor_library_library_year"), "carbon_factor_library", ["library_year"])
    op.create_index(op.f("ix_carbon_factor_library_source_system"), "carbon_factor_library", ["source_system"])

    op.create_table(
        "carbon_factor_category",
        _id_column(),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("source_category_id", sa.String(length=64), nullable=False),
        sa.Column("parent_source_category_id", sa.String(length=64), nullable=True),
        sa.Column("library_year", sa.String(length=16), nullable=True),
        sa.Column("library_code", sa.String(length=32), nullable=True),
        sa.Column("category_name", sa.String(length=255), nullable=False),
        sa.Column("category_path", sa.String(length=1024), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("is_leaf", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carbon_factor_category")),
        sa.UniqueConstraint("source_system", "source_category_id", name="uq_carbon_factor_category_source_id"),
    )
    op.create_index("ix_carbon_factor_category_path", "carbon_factor_category", ["category_path"])
    op.create_index(op.f("ix_carbon_factor_category_category_name"), "carbon_factor_category", ["category_name"])
    op.create_index(op.f("ix_carbon_factor_category_library_code"), "carbon_factor_category", ["library_code"])
    op.create_index(op.f("ix_carbon_factor_category_library_year"), "carbon_factor_category", ["library_year"])
    op.create_index(
        op.f("ix_carbon_factor_category_parent_source_category_id"),
        "carbon_factor_category",
        ["parent_source_category_id"],
    )
    op.create_index(
        op.f("ix_carbon_factor_category_source_category_id"),
        "carbon_factor_category",
        ["source_category_id"],
    )
    op.create_index(op.f("ix_carbon_factor_category_source_system"), "carbon_factor_category", ["source_system"])

    op.create_table(
        "carbon_factor_raw_record",
        _id_column(),
        sa.Column("snapshot_id", sa.String(length=64), nullable=False),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.String(length=512), nullable=True),
        sa.Column("library_year", sa.String(length=16), nullable=True),
        sa.Column("library_code", sa.String(length=32), nullable=True),
        sa.Column("library_name", sa.String(length=255), nullable=True),
        sa.Column("category_path", sa.String(length=1024), nullable=False),
        sa.Column("top_category", sa.String(length=255), nullable=True),
        sa.Column("second_category", sa.String(length=255), nullable=True),
        sa.Column("source_record_id", sa.String(length=128), nullable=True),
        sa.Column("stable_hash", sa.String(length=64), nullable=False),
        sa.Column("factor_name", sa.String(length=1024), nullable=False),
        sa.Column("factor_value_raw", sa.Text(), nullable=True),
        sa.Column("factor_unit_raw", sa.String(length=128), nullable=True),
        sa.Column("region_raw", sa.String(length=255), nullable=True),
        sa.Column("gas_raw", sa.String(length=64), nullable=True),
        sa.Column("time_representativeness", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("source_description", sa.Text(), nullable=True),
        sa.Column("projection_status", sa.String(length=24), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carbon_factor_raw_record")),
        sa.UniqueConstraint(
            "source_system",
            "snapshot_id",
            "stable_hash",
            name="uq_carbon_factor_raw_source_snapshot_hash",
        ),
    )
    op.create_index(
        "ix_carbon_factor_raw_lookup",
        "carbon_factor_raw_record",
        ["source_system", "library_year", "library_code"],
    )
    op.create_index(op.f("ix_carbon_factor_raw_record_category_path"), "carbon_factor_raw_record", ["category_path"])
    op.create_index(op.f("ix_carbon_factor_raw_record_factor_name"), "carbon_factor_raw_record", ["factor_name"])
    op.create_index(
        op.f("ix_carbon_factor_raw_record_factor_unit_raw"),
        "carbon_factor_raw_record",
        ["factor_unit_raw"],
    )
    op.create_index(op.f("ix_carbon_factor_raw_record_gas_raw"), "carbon_factor_raw_record", ["gas_raw"])
    op.create_index(op.f("ix_carbon_factor_raw_record_library_code"), "carbon_factor_raw_record", ["library_code"])
    op.create_index(op.f("ix_carbon_factor_raw_record_library_year"), "carbon_factor_raw_record", ["library_year"])
    op.create_index(
        op.f("ix_carbon_factor_raw_record_projection_status"),
        "carbon_factor_raw_record",
        ["projection_status"],
    )
    op.create_index(op.f("ix_carbon_factor_raw_record_provider"), "carbon_factor_raw_record", ["provider"])
    op.create_index(op.f("ix_carbon_factor_raw_record_region_raw"), "carbon_factor_raw_record", ["region_raw"])
    op.create_index(
        op.f("ix_carbon_factor_raw_record_second_category"),
        "carbon_factor_raw_record",
        ["second_category"],
    )
    op.create_index(op.f("ix_carbon_factor_raw_record_snapshot_id"), "carbon_factor_raw_record", ["snapshot_id"])
    op.create_index(
        op.f("ix_carbon_factor_raw_record_source_record_id"),
        "carbon_factor_raw_record",
        ["source_record_id"],
    )
    op.create_index(op.f("ix_carbon_factor_raw_record_source_system"), "carbon_factor_raw_record", ["source_system"])
    op.create_index(op.f("ix_carbon_factor_raw_record_stable_hash"), "carbon_factor_raw_record", ["stable_hash"])
    op.create_index(op.f("ix_carbon_factor_raw_record_top_category"), "carbon_factor_raw_record", ["top_category"])

    op.create_index(op.f("ix_dataapp_emissionfactor_raw_record_id"), "dataapp_emissionfactor", ["raw_record_id"])
    op.create_index(
        op.f("ix_dataapp_emissionfactor_source_snapshot_id"),
        "dataapp_emissionfactor",
        ["source_snapshot_id"],
    )
    op.create_index(op.f("ix_dataapp_emissionfactor_source_system"), "dataapp_emissionfactor", ["source_system"])
    op.create_foreign_key(
        op.f("fk_dataapp_emissionfactor_raw_record_id_carbon_factor_raw_record"),
        "dataapp_emissionfactor",
        "carbon_factor_raw_record",
        ["raw_record_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_dataapp_emissionfactor_raw_record_id_carbon_factor_raw_record"),
        "dataapp_emissionfactor",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_dataapp_emissionfactor_source_system"), table_name="dataapp_emissionfactor")
    op.drop_index(op.f("ix_dataapp_emissionfactor_source_snapshot_id"), table_name="dataapp_emissionfactor")
    op.drop_index(op.f("ix_dataapp_emissionfactor_raw_record_id"), table_name="dataapp_emissionfactor")
    op.drop_table("carbon_factor_raw_record")
    op.drop_table("carbon_factor_category")
    op.drop_table("carbon_factor_library")
    op.drop_table("carbon_factor_import_batch")
    op.drop_column("dataapp_emissionfactor", "review_status")
    op.drop_column("dataapp_emissionfactor", "projection_status")
    op.drop_column("dataapp_emissionfactor", "raw_record_id")
    op.drop_column("dataapp_emissionfactor", "source_snapshot_id")
    op.drop_column("dataapp_emissionfactor", "source_system")
