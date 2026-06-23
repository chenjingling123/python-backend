"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class SysDictType(Base):
    """
    系统字典类型表 (sys_dict_types)
    """
    __tablename__ = 'sys_dict_types'
    __table_args__ = {'comment': '系统字典类型表'}

    # 主键
    dict_id: Mapped[int] = mapped_column('dict_id', BigInteger, primary_key=True, autoincrement=True, comment='字典ID')

    # 字典类型基本信息
    dict_name: Mapped[Optional[str]] = mapped_column('dict_name', String(64), comment='名称', nullable=True)
    dict_type: Mapped[Optional[str]] = mapped_column('dict_type', String(64), comment='类型', nullable=True)
    status: Mapped[Optional[str]] = mapped_column('status', String(1), comment='状态（0正常 1停用）', nullable=True)

    # 审计字段
    create_by: Mapped[Optional[str]] = mapped_column('create_by', String(191), comment='创建者', nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('create_time', DateTime, comment='创建时间', nullable=True)
    update_by: Mapped[Optional[str]] = mapped_column('update_by', String(191), comment='更新者', nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('update_time', DateTime, comment='更新时间', nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('delete_time', DateTime, comment='删除时间', nullable=True)

    # 备注
    remark: Mapped[Optional[str]] = mapped_column('remark', String(256), comment='备注', nullable=True)

    def __repr__(self):
        return f"<SysDictType(dict_id={self.dict_id}, dict_name='{self.dict_name}', dict_type='{self.dict_type}')>"

    def to_dict(self) -> dict:
        """
        转换为字典格式，对应 C# 的 SysDictTypeModel
        """
        return {
            'dictId': self.dict_id,
            'dictName': self.dict_name,
            'dictType': self.dict_type,
            'status': self.status,
            'createBy': self.create_by,
            'updateBy': self.update_by,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%dT%H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%dT%H:%M:%S') if self.update_time else None,
        }

    def to_dict_with_data(self) -> dict:
        """
        转换为字典格式，包含关联的字典数据
        """
        result = self.to_dict()
        # 添加字典数据列表
        result['dictData'] = [data.to_dict() for data in self.dict_data] if self.dict_data else []
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "SysDictType":
        """
        从字典创建模型实例
        """
        return cls(
            dict_name=data.get('dictName'),
            dict_type=data.get('dictType'),
            status=data.get('status', '0'),
            remark=data.get('remark'),
            create_by=data.get('createBy'),
            update_by=data.get('updateBy')
        )


