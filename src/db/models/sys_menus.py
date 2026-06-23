"""
本文件定义了系统岗位表 (sys_posts) 的数据库模型。
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import BigInteger, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base

class SysMenus(Base):
    """
    系统菜单表 (sys_menus)
    __tablename__ 指定数据库中的表名是 sys_menus
    __table_args__ 设置表的额外属性，这里添加了表注释
    """
    __tablename__ = 'sys_menus'
    __table_args__ = {'comment': '系统菜单表'}

    # 注意：右边mapped_column('menu_name'是数据库里的字段名，左边menuName是要viewmodel映射的alian

    # 主键
    menu_id: Mapped[int] = mapped_column('menu_id', BigInteger, primary_key=True, autoincrement=True,
                                         comment='菜单ID')

    # 菜单基本信息
    menu_name: Mapped[Optional[str]] = mapped_column('menu_name', String(128), comment='菜单名称', nullable=True)
    title: Mapped[Optional[str]] = mapped_column('title', String(64), comment='菜单标题', nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column('parent_id', Integer, comment='父菜单ID', nullable=True)
    sort: Mapped[Optional[int]] = mapped_column('sort', Integer, comment='排序号', nullable=True)
    icon: Mapped[Optional[str]] = mapped_column('icon', String(128), comment='菜单图标', nullable=True)

    # 路由信息
    path: Mapped[Optional[str]] = mapped_column('path', String(128), comment='路由地址', nullable=True)
    component: Mapped[Optional[str]] = mapped_column('component', String(255), comment='组件路径', nullable=True)

    # 菜单属性
    is_frame: Mapped[Optional[str]] = mapped_column('is_frame', String(1), comment='是否为外链（0是 1否）',
                                                    nullable=True)
    is_link: Mapped[Optional[str]] = mapped_column('is_link', String(256), comment='链接地址', nullable=True)
    menu_type: Mapped[Optional[str]] = mapped_column('menu_type', String(1), comment='菜单类型（M目录 C菜单 F按钮）',
                                                     nullable=True)

    # 显示控制
    is_hide: Mapped[Optional[str]] = mapped_column('is_hide', String(1), comment='是否隐藏（0显示 1隐藏）',
                                                   nullable=True)
    is_keep_alive: Mapped[Optional[str]] = mapped_column('is_keep_alive', String(1),
                                                         comment='是否缓存（0缓存 1不缓存）', nullable=True)
    is_affix: Mapped[Optional[str]] = mapped_column('is_affix', String(1),
                                                    comment='是否登录后固定显示在页面顶部sheet', nullable=True)

    # 权限标识
    permission: Mapped[Optional[str]] = mapped_column('permission', String(32), comment='权限标识', nullable=True)

    # 状态信息
    status: Mapped[Optional[str]] = mapped_column('status', String(191), comment='状态（0正常 1停用）', nullable=True)

    # 审计字段
    create_by: Mapped[Optional[str]] = mapped_column('create_by', String(128), comment='创建者', nullable=True)
    create_time: Mapped[Optional[datetime]] = mapped_column('create_time', DateTime, comment='创建时间',
                                                            nullable=True)
    update_by: Mapped[Optional[str]] = mapped_column('update_by', String(128), comment='更新者', nullable=True)
    update_time: Mapped[Optional[datetime]] = mapped_column('update_time', DateTime, comment='更新时间',
                                                            nullable=True)
    delete_time: Mapped[Optional[datetime]] = mapped_column('delete_time', DateTime, comment='删除时间',
                                                            nullable=True)

    # 备注
    remark: Mapped[Optional[str]] = mapped_column('remark', String(191), comment='备注', nullable=True)

