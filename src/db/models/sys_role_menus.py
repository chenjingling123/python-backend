"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class SysRoleMenus(Base):
    """
    系统角色菜单关联表 (sys_role_menus)
    """
    __tablename__ = 'sys_role_menus'
    __table_args__ = {'comment': '系统角色菜单关联表'}

    # 主键
    id: Mapped[int] = mapped_column('id', BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 角色信息
    role_id: Mapped[Optional[int]] = mapped_column('role_id', Integer, comment='角色ID', nullable=True)
    role_name: Mapped[Optional[str]] = mapped_column('role_name', String(128), comment='角色名称', nullable=True)

    # 菜单信息
    menu_id: Mapped[Optional[int]] = mapped_column('menu_id', Integer, comment='菜单ID', nullable=True)

    def __repr__(self):
        return f"<SysRoleMenus(id={self.id}, role_id={self.role_id}, menu_id={self.menu_id})>"

    def to_dict(self) -> dict:
        """
        转换为字典格式
        """
        return {
            'id': self.id,
            'roleId': self.role_id,
            'roleName': self.role_name,
            'menuId': self.menu_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SysRoleMenus":
        """
        从字典创建模型实例
        """
        return cls(
            role_id=data.get('roleId'),
            role_name=data.get('roleName'),
            menu_id=data.get('menuId')
        )