"""
本模块进行数据库初始化和连接管理。
"""
import os
from logging import getLogger

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from config import config

from db.misc import initialize_database

logger = getLogger(__name__)

if config.sqlite.enable:
    logger.info("已启用 SQLite 数据库")
    db_file_path = config.sqlite.file_path
    db_dir = os.path.dirname(db_file_path)

    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"已创建目录: {db_dir}")

    init = not os.path.exists(db_file_path)

    engine = create_engine(
        f"sqlite:///{config.sqlite.file_path}",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    if init:
        initialize_database(engine)
else:
    engine = create_engine(
        f"mysql+pymysql://{config.mysql.username}:{config.mysql.password_quoted}@{config.mysql.host}:{config.mysql.port}/{config.mysql.database}",
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )

