from typing import Optional, Tuple

from sqlalchemy import and_

from db.models.sys_posts import SysPosts
from db import *

class SysPostsService:
    @staticmethod
    def list_sys_posts(
        filters: Optional[dict] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Tuple[int, list[SysPosts]]:
        with Session(engine) as session:

            base_query = session.query(SysPosts)
            sql_filters = []
            
            if filters:
                for key, value in filters.items():
                    if value is None or not hasattr(SysPosts, key):
                        continue

                    if isinstance(value, str):
                        sql_filters.append(getattr(SysPosts, key).like(f'%{value}%'))
                    else:
                        sql_filters.append(getattr(SysPosts, key) == value)

            if sql_filters:
                base_query = base_query.filter(and_(*sql_filters))

            total = base_query.count()

            return total, base_query.offset((page_num - 1) * page_size).limit(page_size).all()

    @staticmethod
    def add_sys_post(sys_post: SysPosts) -> SysPosts:
        with Session(engine) as session:
            session.add(sys_post)
            session.commit()
            session.refresh(sys_post)
            return sys_post

    @staticmethod
    def get_model_info_by_id(id: int) -> Optional[SysPosts]:
        with Session(engine) as session:
            return session.query(SysPosts).filter(SysPosts.id == id).first()

    @staticmethod
    def get_all_sys_posts() -> list[SysPosts]:
        with Session(engine) as session:
            return session.query(SysPosts).all()

    @staticmethod
    def update_sys_post(sys_post: SysPosts) -> Optional[SysPosts]:
        with Session(engine) as session:
            # 1. ��ѯ���ݿ������м�¼
            existing_sys_post = session.query(SysPosts).filter(SysPosts.id == sys_post.id).first()
            if not existing_sys_post:
                return None

            # 2. �����ֶΣ����� SQLAlchemy �ڲ����ԣ�
            for key, value in sys_post.__dict__.items():
                if key.startswith("_"):  # �����ڲ����ԣ��� _sa_instance_state
                    continue
                setattr(existing_sys_post, key, value)

            # 3. �ύ����ˢ��
            session.commit()
            session.refresh(existing_sys_post)
            return existing_sys_post


    @staticmethod
    def delete_model_info(id: int) -> bool:
        with Session(engine) as session:
            model_info = session.query(SysPosts).filter(SysPosts.id == id).first()
            if not model_info:
                return False
            session.delete(model_info)
            session.commit()
            return True
