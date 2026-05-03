import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from app.core.config import settings
from app.db.base import Base
from app.models.booking import Booking  # noqa: F401
from app.models.booking_request import BookingRequest  # noqa: F401
from app.models.chat import Chat  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.package import Package  # noqa: F401
from app.models.package_purchase import PackagePurchase  # noqa: F401
from app.models.password_reset_token import PasswordResetToken  # noqa: F401
from app.models.provider_profile import ProviderProfile  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.revoked_refresh_token import RevokedRefreshToken  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.role_permission import RolePermission  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.subcategory import SubCategory  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.models.user import User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("mysql+aiomysql"):
        return url.replace("mysql+aiomysql", "mysql+pymysql", 1)
    if url.startswith("mysql+asyncmy"):
        return url.replace("mysql+asyncmy", "mysql+pymysql", 1)
    if url.startswith("postgresql+asyncpg"):
        return url.replace("postgresql+asyncpg", "postgresql+psycopg", 1)
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_sync_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_sync_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
