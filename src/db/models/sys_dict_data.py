"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base

class SysDictData(Base):
    """
    系统字典数据表 (sys_dict_data)
    """
    __tablename__ = 'sys_dict_data'
    __table_args__ = {'comment': '系统字典数据表'}

    # 主键
    dict_code: Mapped[int] = mapped_column('dict_code', BigInteger, primary_key=True, autoincrement=True, comment='字典编码')

    # 字典基本信息
    dict_sort: Mapped[Optional[int]] = mapped_column('dict_sort', Integer, comment='排序', nullable=True)
    dict_label: Mapped[Optional[str]] = mapped_column('dict_label', String(64), comment='标签', nullable=True)
    dict_value: Mapped[Optional[str]] = mapped_column('dict_value', String(64), comment='值', nullable=True)
    dict_type: Mapped[Optional[str]] = mapped_column('dict_type', String(64), comment='字典类型', nullable=True)

    # 样式和状态
    css_class: Mapped[Optional[str]] = mapped_column('css_class', String(128), comment='CssClass', nullable=True)
    list_class: Mapped[Optional[str]] = mapped_column('list_class', String(128), comment='ListClass', nullable=True)
    is_default: Mapped[Optional[str]] = mapped_column('is_default', String(8), comment='IsDefault', nullable=True)
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
        return f"<SysDictData(dict_code={self.dict_code}, dict_label='{self.dict_label}')>"

    def to_dict(self) -> dict:
        """
        转换为字典格式，对应 C# 的 SysDictDatumModel
        """
        return {
            'dictCode': self.dict_code,
            'dictSort': self.dict_sort,
            'dictLabel': self.dict_label,
            'dictValue': self.dict_value,
            'dictType': self.dict_type,
            'cssClass': self.css_class,
            'listClass': self.list_class,
            'isDefault': self.is_default,
            'status': self.status,
            'createBy': self.create_by,
            'updateBy': self.update_by,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%dT%H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%dT%H:%M:%S') if self.update_time else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SysDictData":
        """
        从字典创建模型实例
        """
        return cls(
            dict_sort=data.get('dictSort'),
            dict_label=data.get('dictLabel'),
            dict_value=data.get('dictValue'),
            dict_type=data.get('dictType'),
            css_class=data.get('cssClass'),
            list_class=data.get('listClass'),
            is_default=data.get('isDefault'),
            status=data.get('status', '0'),
            remark=data.get('remark'),
            create_by=data.get('createBy'),
            update_by=data.get('updateBy')
        )