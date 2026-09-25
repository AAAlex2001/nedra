"""expertise contract: вид договора, наименование документации и реквизиты заказчика в заявке

Revision ID: 0017
Revises: 0016
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("expertises", sa.Column("object_name", sa.String(500), nullable=True))
    op.add_column("expertises", sa.Column("contract_kind", sa.String(16), nullable=True))

    op.execute("UPDATE expertises SET contract_kind = 'reequipment' WHERE object_code = 'tp'")
    op.execute("UPDATE expertises SET contract_kind = 'declaration' WHERE object_code = 'd'")
    op.execute("UPDATE expertises SET contract_kind = 'justification' WHERE object_code = 'ob'")

    op.create_table(
        "expertise_companies",
        sa.Column(
            "expertise_id",
            sa.Integer(),
            sa.ForeignKey("expertises.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("full_name", sa.String(500), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("inn", sa.String(12), nullable=False),
        sa.Column("kpp", sa.String(9), nullable=True),
        sa.Column("ogrn", sa.String(15), nullable=False),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("bank", sa.String(255), nullable=False),
        sa.Column("bic", sa.String(9), nullable=False),
        sa.Column("account", sa.String(20), nullable=False),
        sa.Column("corr_account", sa.String(20), nullable=False),
        sa.Column("signer_position", sa.String(255), nullable=False),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_genitive", sa.String(500), nullable=False),
        sa.Column("signer_basis", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("expertise_companies")
    op.drop_column("expertises", "contract_kind")
    op.drop_column("expertises", "object_name")
