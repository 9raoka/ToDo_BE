import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from api.database.db import ModelBase
from api.database.models import Task, Done


# Alembic Config オブジェクトの取得
config = context.config

# ロギングの設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# メタデータのターゲット設定
target_metadata = ModelBase.metadata

def run_migrations_offline() -> None:
    """オフラインモードでマイグレーションを実行します。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """オンラインモードでマイグレーションを実行します。"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 型の違いも検出する場合
        compare_server_default=True,  # デフォルト値の違いも検出する場合
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
