from typing import Optional, Tuple

from sqlalchemy import and_

from db import *
from db.models.project_info import ProjectInfo


class ProjectInfoService:
    @staticmethod
    def list_project_info(
        filters: Optional[dict] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Tuple[int, list[ProjectInfo]]:
        with Session(engine) as session:
            base_query = session.query(ProjectInfo).filter(ProjectInfo.delete_time.is_(None))
            sql_filters = []

            if filters:
                for key, value in filters.items():
                    if value is None or not hasattr(ProjectInfo, key):
                        continue

                    if isinstance(value, str):
                        sql_filters.append(getattr(ProjectInfo, key).like(f'%{value}%'))
                    else:
                        sql_filters.append(getattr(ProjectInfo, key) == value)

            if sql_filters:
                base_query = base_query.filter(and_(*sql_filters))

            total = base_query.count()
            rows = base_query.order_by(ProjectInfo.id.desc()).offset((page_num - 1) * page_size).limit(page_size).all()
            return total, rows

    @staticmethod
    def add(project_info: ProjectInfo) -> Optional[ProjectInfo]:
        with Session(engine) as session:
            try:
                project_info.id = None
                session.add(project_info)
                session.flush()
                new_id = project_info.id
                session.commit()
                return session.query(ProjectInfo).filter(ProjectInfo.id == new_id).first()
            except Exception:
                session.rollback()
                raise

    @staticmethod
    def update(project_info: ProjectInfo) -> Optional[ProjectInfo]:
        with Session(engine) as session:
            existing_project = session.query(ProjectInfo).filter(ProjectInfo.id == project_info.id).first()
            if not existing_project:
                return None

            for key, value in project_info.__dict__.items():
                if key.startswith("_"):
                    continue
                setattr(existing_project, key, value)

            session.commit()
            session.refresh(existing_project)
            return existing_project

    @staticmethod
    def delete(project_id: int) -> bool:
        with Session(engine) as session:
            model = session.query(ProjectInfo).filter(ProjectInfo.id == project_id).first()
            if not model:
                return False
            session.delete(model)
            session.commit()
            return True
