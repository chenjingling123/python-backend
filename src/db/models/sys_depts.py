"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import BigInteger, Integer, String, DateTime, CHAR
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class SysDepts(Base):
    """
    系统部门表 (sys_depts)
    """
    __tablename__ = 'sys_depts'
    __table_args__ = {'comment': '系统部门表'}

    # 主键
    dept_id: Mapped[int] = mapped_column('dept_id', BigInteger, primary_key=True, autoincrement=True,
                                         comment='部门ID')

    # 部门关系
    parent_id: Mapped[Optional[int]] = mapped_column('parent_id', Integer, comment='上级部门', nullable=True)
    dept_path: Mapped[Optional[str]] = mapped_column('dept_path', String(255), comment='部门路径', nullable=True)

    # 部门基本信息
    dept_name: Mapped[Optional[str]] = mapped_column('dept_name', String(128), comment='部门名称', nullable=True)
    sort: Mapped[Optional[int]] = mapped_column('sort', Integer, comment='排序', nullable=True)

    # 负责人信息
    leader: Mapped[Optional[str]] = mapped_column('leader', String(64), comment='负责人', nullable=True)
    phone: Mapped[Optional[str]] = mapped_column('phone', String(11), comment='手机', nullable=True)
    email: Mapped[Optional[str]] = mapped_column('email', String(64), comment='邮箱', nullable=True)

    # 状态信息
    status: Mapped[Optional[str]] = mapped_column('status', CHAR(1), comment='状态（0正常 1停用）', nullable=True)

    # 审计字段
    create_by: Mapped[Optional[str]] = mapped_column('create_by', String(64), comment='创建人', nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('create_time', DateTime, comment='创建时间',
                                                            nullable=True)
    update_by: Mapped[Optional[str]] = mapped_column('update_by', String(64), comment='修改人', nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('update_time', DateTime, comment='更新时间',
                                                            nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('delete_time', DateTime, comment='删除时间',
                                                            nullable=True)

    def __repr__(self):
        return f"<SysDepts(dept_id={self.dept_id}, dept_name='{self.dept_name}')>"

    def to_dict(self) -> dict:
        """
        转换为字典格式，对应 C# 的 SysDeptsModel
        """
        return {
            'deptId': self.dept_id,
            'parentId': self.parent_id,
            'deptPath': self.dept_path,
            'deptName': self.dept_name,
            'sort': self.sort,
            'leader': self.leader,
            'phone': self.phone,
            'email': self.email,
            'status': self.status,
            'createBy': self.create_by,
            'updateBy': self.update_by,
            'create_time': self.create_time.strftime('%Y-%m-%dT%H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%dT%H:%M:%S') if self.update_time else None,
            'children': []  # 子部门会在构建树时填充
        }

    def to_dict_with_children(self, children: List[dict] = None) -> dict:
        """
        转换为字典格式，包含子部门

        Args:
            children: 子部门列表

        Returns:
            包含子部门的部门字典
        """
        result = self.to_dict()
        result['children'] = children or []
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "SysDepts":
        """
        从字典创建模型实例
        """
        return cls(
            parent_id=data.get('parentId'),
            dept_path=data.get('deptPath'),
            dept_name=data.get('deptName'),
            sort=data.get('sort'),
            leader=data.get('leader'),
            phone=data.get('phone'),
            email=data.get('email'),
            status=data.get('status', '0'),
            create_by=data.get('createBy'),
            update_by=data.get('updateBy')
        )
