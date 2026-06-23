"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class SysUsers(Base):
    """
    系统用户表 (sys_users)
    """
    __tablename__ = 'sys_users'
    __table_args__ = {'comment': '系统用户表'}

    # 主键
    user_id: Mapped[int] = mapped_column('user_id', BigInteger, primary_key=True, autoincrement=True, comment='用户ID')

    # 用户基本信息
    username: Mapped[Optional[str]] = mapped_column('username', String(64), comment='用户名', nullable=True)
    password: Mapped[Optional[str]] = mapped_column('password', String(128), comment='密码', nullable=True)
    salt: Mapped[Optional[str]] = mapped_column('salt', String(255), comment='密码盐值', nullable=True)
    nick_name: Mapped[Optional[str]] = mapped_column('nick_name', String(128), comment='昵称', nullable=True)

    # 联系信息
    phone: Mapped[Optional[str]] = mapped_column('phone', String(11), comment='手机号', nullable=True)
    email: Mapped[Optional[str]] = mapped_column('email', String(128), comment='邮箱', nullable=True)

    # 个人信息
    avatar: Mapped[Optional[str]] = mapped_column('avatar', String(255), comment='头像', nullable=True)
    sex: Mapped[Optional[str]] = mapped_column('sex', String(255), comment='性别', nullable=True)

    # 组织关系
    dept_id: Mapped[Optional[int]] = mapped_column('dept_id', Integer, comment='部门ID', nullable=True)
    role_id: Mapped[Optional[int]] = mapped_column('role_id', Integer, comment='角色ID', nullable=True)
    role_ids: Mapped[Optional[str]] = mapped_column('role_ids', String(255), comment='多角色ID，用逗号分隔',
                                                    nullable=True)
    post_id: Mapped[Optional[int]] = mapped_column('post_id', Integer, comment='岗位ID', nullable=True)
    post_ids: Mapped[Optional[str]] = mapped_column('post_ids', String(255), comment='多岗位ID，用逗号分隔',
                                                    nullable=True)

    # 状态信息
    status: Mapped[Optional[str]] = mapped_column('status', String(1), comment='状态（0正常 1停用）', nullable=True)

    # 审计字段
    create_by: Mapped[Optional[str]] = mapped_column('create_by', String(128), comment='创建者', nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('create_time', DateTime, comment='创建时间', nullable=True)
    update_by: Mapped[Optional[str]] = mapped_column('update_by', String(128), comment='更新者', nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('update_time', DateTime, comment='更新时间', nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('delete_time', DateTime, comment='删除时间', nullable=True)

    # 备注
    remark: Mapped[Optional[str]] = mapped_column('remark', String(255), comment='备注', nullable=True)

