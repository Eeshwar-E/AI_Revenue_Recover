"""Initial schema: create all tables (Postgres)."""
from alembic import op
import sqlalchemy as sa  # noqa: F401
from app.models import Base  # noqa: F401 registers metadata

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
