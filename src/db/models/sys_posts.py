"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base

class SysPosts(Base):
    """
    系统岗位表 (sys_posts)
    对应数据库表：sys_posts
    字段映射规则：Python属性名(驼峰) -> 数据库字段名(下划线)
    """
    __tablename__ = 'sys_posts'
    __table_args__ = {'comment': '系统岗位表'}

    # 主键
    post_id: Mapped[int] = mapped_column('post_id', BigInteger, primary_key=True, autoincrement=True, comment='岗位ID')

    # 岗位基本信息
    post_name: Mapped[Optional[str]] = mapped_column('post_name', String(128), comment='岗位名称', nullable=True)
    post_code: Mapped[Optional[str]] = mapped_column('post_code', String(128), comment='岗位代码', nullable=True)
    sort: Mapped[Optional[int]] = mapped_column('sort', Integer, comment='岗位排序', nullable=True)
    status: Mapped[Optional[str]] = mapped_column('status', String(1), comment='状态（0正常 1停用）', nullable=True)
    remark: Mapped[Optional[str]] = mapped_column('remark', String(255), comment='描述', nullable=True)

    # 审计字段
    create_by: Mapped[Optional[str]] = mapped_column('create_by', String(128), comment='创建者', nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('create_time', DateTime, comment='创建时间', nullable=True)
    update_by: Mapped[Optional[str]] = mapped_column('update_by', String(128), comment='更新者', nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('update_time', DateTime, comment='更新时间', nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('delete_time', DateTime, comment='删除时间', nullable=True)
