from typing import Optional, Tuple

from sqlalchemy import and_

from db.models.falldown_device import FalldownDevice
from db import *

class FalldownDeviceService:
    @staticmethod
    def list_falldown_device(
        filters: Optional[dict] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Tuple[int, list[FalldownDevice]]:
        with Session(engine) as session:

            base_query = session.query(FalldownDevice)
            sql_filters = []
            
            if filters:
                for key, value in filters.items():
                    if value is None or not hasattr(FalldownDevice, key):
                        continue

                    if isinstance(value, str):
                        sql_filters.append(getattr(FalldownDevice, key).like(f'%{value}%'))
                    else:
                        sql_filters.append(getattr(FalldownDevice, key) == value)

            if sql_filters:
                base_query = base_query.filter(and_(*sql_filters))

            total = base_query.count()

            return total, base_query.offset((page_num - 1) * page_size).limit(page_size).all()

    @staticmethod
    def add(falldown_device: FalldownDevice) -> Optional[FalldownDevice]:
        """
        添加跌倒设备
        Args:
            falldown_device: 设备对象
        Returns:
            添加后的设备对象，失败返回None
        """
        with Session(engine) as session:
            try:
                # 确保Id为None（自增主键）
                falldown_device.Id = None

                # 添加到会话
                session.add(falldown_device)

                # flush到数据库以获取Id
                session.flush()
                new_id = falldown_device.Id
                print(f"Flush后获取到Id: {new_id}")

                # 提交事务
                session.commit()

                # 重新查询获取完整对象（避免refresh问题）
                fresh_device = session.query(FalldownDevice).filter(
                    FalldownDevice.Id == new_id
                ).first()

                if fresh_device:
                    print(f"重新查询成功，Id: {fresh_device.Id}")
                    return fresh_device
                else:
                    print("警告：重新查询失败，返回原对象")
                    return falldown_device

            except Exception as e:
                session.rollback()
                print(f"添加失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return None



    @staticmethod
    def get_by_id(id: int) -> Optional[FalldownDevice]:
        with Session(engine) as session:
            return session.query(FalldownDevice).filter(FalldownDevice.id == id).first()

    @staticmethod
    def get_all_falldown_device() -> list[FalldownDevice]:
        with Session(engine) as session:
            return session.query(FalldownDevice).all()

    @staticmethod
    def update(falldown_device: FalldownDevice) -> Optional[FalldownDevice]:
        with Session(engine) as session:
            # 1. ��ѯ���ݿ������м�¼
            existing_falldown_device = session.query(FalldownDevice).filter(FalldownDevice.Id == falldown_device.Id).first()
            if not existing_falldown_device:
                return None

            # 2. �����ֶΣ����� SQLAlchemy �ڲ����ԣ�
            for key, value in falldown_device.__dict__.items():
                if key.startswith("_"):  # �����ڲ����ԣ��� _sa_instance_state
                    continue
                setattr(existing_falldown_device, key, value)

            # 3. �ύ����ˢ��
            session.commit()
            session.refresh(existing_falldown_device)
            return existing_falldown_device


    @staticmethod
    def delete(Id: int) -> bool:
        with Session(engine) as session:
            model = session.query(FalldownDevice).filter(FalldownDevice.Id == Id).first()
            if not model:
                return False
            session.delete(model)
            session.commit()
            return True
