from logging import getLogger

from sqlalchemy.orm import Session

from db.models.base import Base

logger = getLogger(__name__)

def initialize_database(engine):
    logger.info("正在初始化数据库...")
    _create_tables(engine)
    _init_label_class(engine)
    logger.info("数据库初始化完成.")


def _create_tables(engine):
    Base.metadata.create_all(engine)


def _init_label_class(engine):
    """
    初始化默认标签类别
    
    :note: 暂时省略了类别图片的初始化
    """

    default_classes = [
    ]

    with Session(engine) as session:
        session.add_all(default_classes)
        session.commit()
        logger.info("已初始化默认标签类别")
