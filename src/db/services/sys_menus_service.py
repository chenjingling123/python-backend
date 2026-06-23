from typing import Optional, Tuple, Any, List, Dict
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.models.sys_menus import SysMenus  # 导入 SysMenus 模型
from db import engine


class SysMenusService:
    """系统菜单服务类"""

    @staticmethod
    def get_sys_menus_by_role_ids(role_ids: str) -> List[SysMenus]:
        """
        根据角色ID字符串获取菜单列表

        Args:
            role_ids: 角色ID字符串，例如 "1,2,3"

        Returns:
            菜单列表
        """
        from db.models.sys_role_menus import SysRoleMenus

        with Session(engine) as session:
            # 解析角色ID
            role_id_list = [int(rid.strip()) for rid in role_ids.split(',') if rid.strip()]

            if not role_id_list:
                return []

            # 使用子查询 - 注意字段名是 menu_id (SysRoleMenus中使用的是下划线命名)
            subquery = session.query(SysRoleMenus.menu_id).filter(
                SysRoleMenus.role_id.in_(role_id_list)
            ).distinct().subquery()

            # 主查询 - SysMenus.menuId 对应数据库的 menu_id 字段
            menus = session.query(SysMenus).filter(
                SysMenus.menu_id.in_(subquery),  # menuId 是 Python 属性名，映射到数据库的 menu_id
                SysMenus.delete_time.is_(None)
            ).order_by(SysMenus.sort).all()

            return menus

    @staticmethod
    def get_sys_menus_by_role_ids_v4(role_ids: str) -> List[SysMenus]:
        """
        根据角色ID字符串获取菜单列表

        Args:
            role_ids: 角色ID字符串，例如 "1,2,3"

        Returns:
            菜单列表
        """
        with Session(engine) as session:
            # 方法1：使用原生SQL查询（最接近C#代码）
            str_sql = f"""
                SELECT * FROM sys_menus 
                WHERE menu_id IN (
                    SELECT DISTINCT menu_id FROM sys_role_menus 
                    WHERE role_id IN ({role_ids})
                )
                AND delete_time IS NULL  -- 只查询未删除的菜单
            """
            result = session.execute(text(str_sql))
            menus = [SysMenus(**row) for row in result.mappings().all()]
            return menus

    @staticmethod
    def get_sys_menus_by_role_ids_v2(role_ids: str) -> List[SysMenus]:
        """
        根据角色ID字符串获取菜单列表（使用SQLAlchemy ORM方式）

        Args:
            role_ids: 角色ID字符串，例如 "1,2,3"

        Returns:
            菜单列表
        """
        with Session(engine) as session:
            # 假设有 sys_role_menus 表模型
            from db.models.sys_role_menus import SysRoleMenus  # 导入角色菜单关联表模型

            # 解析角色ID列表
            role_id_list = [int(rid.strip()) for rid in role_ids.split(',') if rid.strip()]

            if not role_id_list:
                return []

            # 使用子查询
            subquery = session.query(SysRoleMenus.menu_id).filter(
                SysRoleMenus.role_id.in_(role_id_list)
            ).distinct().subquery()

            # 主查询
            menus = session.query(SysMenus).filter(
                SysMenus.menu_id.in_(subquery),
                SysMenus.delete_time.is_(None)  # 只查询未删除的菜单
            ).order_by(SysMenus.sort).all()

            return menus

    @staticmethod
    def get_sys_menus_by_role_ids_v3(role_ids: List[int]) -> List[SysMenus]:
        """
        根据角色ID列表获取菜单列表（推荐使用，参数为列表）

        Args:
            role_ids: 角色ID列表，例如 [1, 2, 3]

        Returns:
            菜单列表
        """
        with Session(engine) as session:
            if not role_ids:
                return []

            # 假设有 sys_role_menus 表模型
            from db.models.sys_role_menus import SysRoleMenus  # 导入角色菜单关联表模型

            # 使用子查询
            subquery = session.query(SysRoleMenus.menu_id).filter(
                SysRoleMenus.role_id.in_(role_ids)
            ).distinct().subquery()

            # 主查询
            menus = session.query(SysMenus).filter(
                SysMenus.menu_id.in_(subquery),
                SysMenus.delete_time.is_(None)
            ).order_by(SysMenus.sort).all()

            return menus

    @staticmethod
    def menus_to_dict_list(menus: List[SysMenus]) -> List[Dict]:
        """
        将菜单列表转换为字典列表

        Args:
            menus: 菜单对象列表

        Returns:
            字典列表
        """
        result = []
        for menu in menus:
            menu_dict = {
                'menu_id': menu.menu_id,
                'menu_name': menu.menu_name,
                'title': menu.title,
                'parent_id': menu.parent_id,
                'sort': menu.sort,
                'icon': menu.icon,
                'path': menu.path,
                'component': menu.component,
                'is_frame': menu.is_frame,
                'is_link': menu.is_link,
                'menu_type': menu.menu_type,
                'is_hide': menu.is_hide,
                'is_keep_alive': menu.is_keep_alive,
                'is_affix': menu.is_affix,
                'permission': menu.permission,
                'status': menu.status,
                'create_by': menu.create_by,
                'update_by': menu.update_by,
                'remark': menu.remark,
                'create_time': menu.create_time.strftime('%Y-%m-%d %H:%M:%S') if menu.create_time else None,
                'update_time': menu.update_time.strftime('%Y-%m-%d %H:%M:%S') if menu.update_time else None,
                'delete_time': menu.delete_time.strftime('%Y-%m-%d %H:%M:%S') if menu.delete_time else None
            }
            result.append(menu_dict)
        return result

    @staticmethod
    def get_menus_tree(menus: List[SysMenus], parent_id: int = 0) -> List[Dict]:
        """
        构建菜单树（根据C#代码逻辑转换）

        Args:
            menus: 菜单列表
            parent_id: 父菜单ID

        Returns:
            菜单树列表（前端路由格式）
        """
        tree = []

        for menu in menus:
            if menu.parent_id != parent_id:
                continue

            # 基础字段映射
            menu_item = {
                'name': menu.menu_name,  # C#: menu.name = one.MenuName
                'path': menu.path or '',  # C#: menu.path = one.Path
                'redirect': '',  # C#: menu.redirect = ""
                'component': menu.component or '',  # C#: menu.component = one.Component
                'sort': menu.sort or 0,  # C#: menu.sort = one.Sort
                'meta': {},  # 先创建空的meta
                'children': []  # 特别注意：C#代码强调children不能为null，所以必须初始化为空列表
            }

            # 构建meta对象（对应C#的MenuMeta）
            meta = {}

            # auth字段（C#中注释说数据来源待定，这里从permission字段获取）
            if menu.permission and menu.permission.strip():
                meta['auth'] = [menu.permission.strip()]
            else:
                meta['auth'] = []

            # icon字段
            meta['icon'] = menu.icon or ''

            # is_affix（默认false，只有为"1"时才为true）
            meta['is_affix'] = False  # 默认值
            if menu.is_affix and menu.is_affix == '1':
                meta['is_affix'] = True

            # is_frame（默认false，只有为"1"时才为true）
            meta['is_frame'] = False  # 默认值
            if menu.is_frame and menu.is_frame == '1':
                meta['is_frame'] = True

            # is_hide（默认false，只有为"1"时才为true）
            meta['is_hide'] = False  # 默认值
            if menu.is_hide and menu.is_hide == '1':
                meta['is_hide'] = True

            # is_keep_alive（默认false，只有为"1"时才为true）
            meta['is_keep_alive'] = False  # 默认值
            if menu.is_keep_alive and menu.is_keep_alive == '1':
                meta['is_keep_alive'] = True

            # is_link
            meta['is_link'] = menu.is_link or ''

            # title字段（如果title为空则用menu_name代替）
            if menu.title and menu.title.strip():
                meta['title'] = menu.title
            else:
                meta['title'] = menu.menu_name  # C#: string.IsNullOrEmpty(one.Title) ? one.MenuName : one.Title

            menu_item['meta'] = meta

            # 递归获取子菜单（对应C#的递归调用）
            children = SysMenusService.get_menus_tree(menus, menu.menu_id)
            menu_item['children'] = children  # 即使children为空也是空列表，不会为null

            tree.append(menu_item)

        # 按sort字段排序（对应C#的target.Sort()）
        tree.sort(key=lambda x: x.get('sort', 0))

        return tree

    @staticmethod
    def get_permissions_by_role_ids(role_ids: List[int]) -> List[str]:
        """
        根据角色ID列表获取权限列表

        Args:
            role_ids: 角色ID列表

        Returns:
            权限列表
        """
        menus = SysMenusService.get_sys_menus_by_role_ids_v3(role_ids)

        permissions = []
        for menu in menus:
            if menu.permission and menu.permission.strip():
                permissions.append(menu.permission.strip())

        return permissions

    @staticmethod
    def get_menus_and_permissions_by_role_ids(role_ids: List[int]) -> Tuple[List[Dict], List[str]]:
        """
        根据角色ID列表获取菜单树和权限列表

        Args:
            role_ids: 角色ID列表

        Returns:
            (菜单树列表, 权限列表)
        """
        menus = SysMenusService.get_sys_menus_by_role_ids_v3(role_ids)

        # 收集权限
        permissions = []
        for menu in menus:
            if menu.permission and menu.permission.strip():
                permissions.append(menu.permission.strip())

        # 构建菜单树
        menu_tree = SysMenusService.get_menus_tree(menus)

        return menu_tree, permissions

    @staticmethod
    def get_router_format_by_role_ids(role_ids: List[int]) -> List[Dict]:
        """
        根据角色ID列表获取前端路由格式的菜单

        Args:
            role_ids: 角色ID列表

        Returns:
            前端路由格式的菜单列表
        """
        menus = SysMenusService.get_sys_menus_by_role_ids_v3(role_ids)

        # 转换为前端路由格式
        router_menus = []
        for menu in menus:
            if menu.menu_type and menu.menu_type.upper() == 'F':
                continue  # 过滤掉按钮类型

            router_item = menu.to_router_format() if hasattr(menu, 'to_router_format') else {
                'name': menu.menu_name,
                'path': menu.path or '',
                'redirect': '',
                'component': 'Layout' if menu.menu_type == 'M' else menu.component or '',
                'sort': menu.sort or 0,
                'meta': {
                    'title': menu.title or menu.menu_name,
                    'isLink': menu.is_link or '',
                    'isHide': menu.is_hide == '1',
                    'isKeepAlive': menu.is_keep_alive == '0',
                    'isAffix': menu.is_affix == '1',
                    'isFrame': menu.is_frame == '0',
                    'auth': [menu.permission] if menu.permission else [],
                    'icon': menu.icon or ''
                },
                'children': []
            }
            router_menus.append(router_item)

        # 构建树形结构
        def build_tree(items, parent_id=0):
            tree = []
            for item in items:
                menu_obj = next((m for m in menus if m.menu_id == item.get('menu_id')), None)
                if menu_obj and menu_obj.parent_id == parent_id:
                    item['children'] = build_tree(items, menu_obj.menu_id)
                    tree.append(item)
            return tree

        return build_tree(router_menus)

    # 在现有的 SysMenusService 类中添加以下方法

    @staticmethod
    def get_all_menus() -> List[SysMenus]:
        """获取所有菜单（未删除的）"""
        with Session(engine) as session:
            return session.query(SysMenus).filter(
                SysMenus.delete_time.is_(None)
            ).order_by(SysMenus.sort).all()

    @staticmethod
    def get_menu_list(menu_name: Optional[str] = None, status: Optional[str] = None) -> List[SysMenus]:
        """根据条件获取菜单列表"""
        with Session(engine) as session:
            query = session.query(SysMenus).filter(SysMenus.delete_time.is_(None))

            if menu_name:
                query = query.filter(SysMenus.menu_name.like(f'%{menu_name}%'))

            if status:
                query = query.filter(SysMenus.status == status)

            return query.order_by(SysMenus.sort).all()

    @staticmethod
    def get_menu_by_id(menu_id: int) -> Optional[SysMenus]:
        """根据ID获取菜单"""
        with Session(engine) as session:
            return session.query(SysMenus).filter(
                SysMenus.menu_id == menu_id,
                SysMenus.delete_time.is_(None)
            ).first()

    @staticmethod
    def build_menu_tree(menus: List[SysMenus], parent_id: int = 0) -> List[Dict]:
        """构建菜单树（用于选择器）"""
        tree = []

        for menu in menus:
            if menu.parent_id != parent_id:
                continue

            node = {
                'id': menu.menu_id,
                'label': menu.title or menu.menu_name,
                'children': []
            }

            children = SysMenusService.build_menu_tree(menus, menu.menu_id)
            if children:
                node['children'] = children

            tree.append(node)

        # 按sort排序
        tree.sort(key=lambda x: next(
            (menu.sort for menu in menus if menu.menu_id == x['id']), 0
        ))

        return tree

    @staticmethod
    def get_menu_ids_by_role_id(role_id: int) -> List[int]:
        """根据角色ID获取已分配的菜单ID列表"""
        from db.models.sys_role_menus import SysRoleMenus

        with Session(engine) as session:
            result = session.query(SysRoleMenus.menu_id).filter(
                SysRoleMenus.role_id == role_id
            ).all()
            return [r[0] for r in result]

    @staticmethod
    def has_child_menus(menu_id: int) -> bool:
        """检查是否有子菜单"""
        with Session(engine) as session:
            count = session.query(SysMenus).filter(
                SysMenus.parent_id == menu_id,
                SysMenus.delete_time.is_(None)
            ).count()
            return count > 0

    @staticmethod
    def is_menu_assigned_to_role(menu_id: int) -> bool:
        """检查菜单是否已分配给角色"""
        from db.models.sys_role_menus import SysRoleMenus

        with Session(engine) as session:
            count = session.query(SysRoleMenus).filter(
                SysRoleMenus.menu_id == menu_id
            ).count()
            return count > 0

    @staticmethod
    def check_menu_name_unique(menu_name: str, parent_id: int, menu_id: int = 0) -> bool:
        """检查菜单名称是否唯一"""
        with Session(engine) as session:
            query = session.query(SysMenus).filter(
                SysMenus.menu_name == menu_name,
                SysMenus.parent_id == parent_id,
                SysMenus.delete_time.is_(None)
            )

            if menu_id > 0:
                query = query.filter(SysMenus.menu_id != menu_id)

            count = query.count()
            return count == 0

    @staticmethod
    def add_menu(menu: SysMenus) -> Tuple[bool, Any]:
        """添加菜单"""
        from db import engine
        from sqlalchemy.exc import IntegrityError

        with Session(engine) as session:
            try:
                session.add(menu)
                session.commit()
                session.refresh(menu)
                return True, menu
            except IntegrityError as e:
                session.rollback()
                return False, f"数据完整性错误: {str(e)}"
            except Exception as e:
                session.rollback()
                return False, str(e)

    @staticmethod
    def update_menu(menu_id: int, update_data: Dict) -> Tuple[bool, Any]:
        """更新菜单"""
        from db import engine

        with Session(engine) as session:
            try:
                menu = session.query(SysMenus).filter(
                    SysMenus.menu_id == menu_id
                ).first()

                if not menu:
                    return False, "菜单不存在"

                for key, value in update_data.items():
                    if hasattr(menu, key):
                        setattr(menu, key, value)

                session.commit()
                session.refresh(menu)
                return True, menu
            except Exception as e:
                session.rollback()
                return False, str(e)

    @staticmethod
    def delete_menu(menu_id: int) -> Tuple[bool, str]:
        """删除菜单（软删除）"""
        from db import engine

        with Session(engine) as session:
            try:
                menu = session.query(SysMenus).filter(
                    SysMenus.menu_id == menu_id
                ).first()

                if not menu:
                    return False, "菜单不存在"

                menu.delete_time = datetime.now()
                session.commit()
                return True, "删除成功"
            except Exception as e:
                session.rollback()
                return False, str(e)

    @staticmethod
    def build_frontend_menu_tree(menus: List[SysMenus], parent_id: int = 0) -> List[Dict]:
        """
        构建前端需要的菜单树结构（完全匹配你给的JSON）
        """
        tree = []

        for menu in menus:
            if (menu.parent_id or 0) != parent_id:
                continue

            node = {
                "menuId": menu.menu_id,
                "menuName": menu.menu_name,
                "title": menu.title or "",
                "parentId": menu.parent_id or 0,
                "sort": menu.sort or 0,
                "icon": menu.icon or "",
                "path": menu.path or "",
                "component": menu.component or "",
                "isFrame": menu.is_frame or "",
                "isLink": menu.is_link or "",
                "menuType": menu.menu_type or "",
                "isHide": menu.is_hide or "0",
                "isKeepAlive": menu.is_keep_alive or "",
                "isAffix": menu.is_affix or "",
                "permission": menu.permission or "",
                "status": menu.status or "0",
                "createBy": menu.create_by or "",
                "update_by": menu.update_by,  # 保持 null
                "remark": menu.remark or "",
                "create_time": None,
                "update_time": None
            }

            # 递归 children
            children = SysMenusService.build_frontend_menu_tree(menus, menu.menu_id)

            # ⚠️ 关键点：子节点为空时 = null（不是 []）
            node["children"] = children if children else None

            tree.append(node)

        # 排序
        tree.sort(key=lambda x: x["sort"])

        return tree