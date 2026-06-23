# services/sys_depts_service.py
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from db.models.sys_depts import SysDepts
from db import engine


class SysDeptsService:
    """系统部门服务类"""

    @staticmethod
    def get_dept_tree() -> Dict[str, Any]:
        """
        获取部门树（对应 C# 的 GetDeptTree 方法）

        Returns:
            返回格式：{"code": 200, "msg": "success", "data": [...]}
        """
        try:
            with Session(engine) as session:
                # 查询所有部门，按部门名称排序（对应 C# 的 r => r.DeptName, true）
                records = session.query(SysDepts).filter(
                    SysDepts.delete_time.is_(None)
                ).order_by(SysDepts.dept_name.asc()).all()

                # 构建部门树
                top_parent_id = 0  # 父节点0表示根节点
                listdata = SysDeptsService._get_sub_depts(records, top_parent_id)

                return {
                    'code': 200,
                    'msg': 'success',
                    'data': listdata
                }

        except Exception as e:
            return {
                'code': 500,
                'msg': f'获取部门树失败: {str(e)}',
                'data': []
            }

    @staticmethod
    def _get_sub_depts(src: List[SysDepts], parent_id: int) -> List[Dict]:
        """
        递归生成部门树（对应 C# 的 GetSubDepts 方法）

        Args:
            src: 所有部门列表
            parent_id: 父部门ID

        Returns:
            部门树列表
        """
        target = []

        for one in src:
            if one.parent_id == parent_id:
                # 构建部门节点
                row = {
                    'deptId': one.dept_id,
                    'parentId': one.parent_id,
                    'deptPath': one.dept_path,
                    'deptName': one.dept_name,
                    'sort': one.sort,
                    'leader': one.leader,
                    'phone': one.phone,
                    'email': one.email,
                    'status': one.status,
                    'createBy': one.create_by,
                    'updateBy': one.update_by,
                    'create_time': one.create_time.strftime('%Y-%m-%dT%H:%M:%S') if one.create_time else None,
                    'update_time': one.update_time.strftime('%Y-%m-%dT%H:%M:%S') if one.update_time else None,
                    'children': []
                }

                # 递归获取子部门
                children = SysDeptsService._get_sub_depts(src, one.dept_id)
                if children:
                    row['children'] = children

                target.append(row)

        # 按 sort 排序
        target.sort(key=lambda x: x.get('sort', 0))
        return target

    @staticmethod
    def get_table_data() -> Dict[str, Any]:
        """
        获取表格数据（对应 C# 的 GetTableData 方法）

        Returns:
            部门树数据
        """
        return SysDeptsService.get_dept_tree()

    @staticmethod
    def get_role_dept_tree(role_id: int) -> Dict[str, Any]:
        """
        根据角色ID获取部门树（对应 C# 的 GetRoleDeptTree 方法）

        Args:
            role_id: 角色ID

        Returns:
            返回格式：{"code": 200, "msg": "success", "data": {"checkedKeys": [...], "depts": [...]}}
        """
        try:
            with Session(engine) as session:
                # 查询角色关联的部门
                # 假设有 SysRoleDept 模型
                from db.models.sys_role_depts import SysRoleDept

                role_depts_list = session.query(SysRoleDept).filter(
                    SysRoleDept.role_id == role_id
                ).all()

                # 构建部门查询条件
                query = session.query(SysDepts).filter(SysDepts.delete_time.is_(None))

                if role_depts_list:
                    # 如果有角色关联的部门，只查询这些部门
                    dept_ids = [rd.dept_id for rd in role_depts_list]
                    query = query.filter(SysDepts.dept_id.in_(dept_ids))

                # 查询部门列表
                records = query.order_by(SysDepts.dept_id.asc()).all()

                # 构建部门树
                parent_id = 0
                dept_tree = SysDeptsService._get_sub_depts(records, parent_id)

                # 获取已选中的部门ID
                checked_keys = []
                if role_depts_list:
                    checked_keys = [rd.dept_id for rd in role_depts_list]

                return {
                    'code': 200,
                    'msg': 'success',
                    'data': {
                        'checkedKeys': checked_keys,
                        'depts': dept_tree
                    }
                }

        except ImportError:
            # 如果没有 SysRoleDept 模型，返回空数据
            return {
                'code': 200,
                'msg': 'success',
                'data': {
                    'checkedKeys': [],
                    'depts': []
                }
            }
        except Exception as e:
            return {
                'code': 500,
                'msg': f'获取角色部门树失败: {str(e)}',
                'data': {
                    'checkedKeys': [],
                    'depts': []
                }
            }

    @staticmethod
    def get_dept_by_id(dept_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取部门

        Args:
            dept_id: 部门ID

        Returns:
            部门数据
        """
        with Session(engine) as session:
            dept = session.query(SysDepts).filter(
                SysDepts.dept_id == dept_id,
                SysDepts.delete_time.is_(None)
            ).first()

            if dept:
                return {
                    'deptId': dept.dept_id,
                    'parentId': dept.parent_id,
                    'deptPath': dept.dept_path,
                    'deptName': dept.dept_name,
                    'sort': dept.sort,
                    'leader': dept.leader,
                    'phone': dept.phone,
                    'email': dept.email,
                    'status': dept.status,
                    'createBy': dept.create_by,
                    'updateBy': dept.update_by,
                    'create_time': dept.create_time.strftime('%Y-%m-%dT%H:%M:%S') if dept.create_time else None,
                    'update_time': dept.update_time.strftime('%Y-%m-%dT%H:%M:%S') if dept.update_time else None
                }
            return None

    @staticmethod
    def add_dept(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        添加部门

        Args:
            data: 部门数据

        Returns:
            (是否成功, 消息, 数据)
        """
        with Session(engine) as session:
            try:
                # 检查同级部门下是否有重名
                existing = session.query(SysDepts).filter(
                    SysDepts.dept_name == data.get('deptName'),
                    SysDepts.parent_id == data.get('parentId', 0),
                    SysDepts.delete_time.is_(None)
                ).first()

                if existing:
                    return False, "同级部门下已存在相同名称", None

                new_dept = SysDepts(
                    parent_id=data.get('parentId'),
                    dept_path=data.get('deptPath'),
                    dept_name=data.get('deptName'),
                    sort=data.get('sort'),
                    leader=data.get('leader'),
                    phone=data.get('phone'),
                    email=data.get('email'),
                    status=data.get('status', '0'),
                    create_by=data.get('createBy'),
                    create_time=datetime.now()
                )

                session.add(new_dept)
                session.commit()
                session.refresh(new_dept)

                return True, "添加成功", {
                    'deptId': new_dept.dept_id,
                    'parentId': new_dept.parent_id,
                    'deptPath': new_dept.dept_path,
                    'deptName': new_dept.dept_name,
                    'sort': new_dept.sort,
                    'leader': new_dept.leader,
                    'phone': new_dept.phone,
                    'email': new_dept.email,
                    'status': new_dept.status,
                    'createBy': new_dept.create_by,
                    'updateBy': new_dept.update_by,
                    'create_time': new_dept.create_time.strftime('%Y-%m-%dT%H:%M:%S') if new_dept.create_time else None,
                    'update_time': None
                }

            except Exception as e:
                session.rollback()
                return False, f"添加失败: {str(e)}", None

    @staticmethod
    def update_dept(dept_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        更新部门

        Args:
            dept_id: 部门ID
            data: 要更新的数据

        Returns:
            (是否成功, 消息, 数据)
        """
        with Session(engine) as session:
            try:
                existing = session.query(SysDepts).filter(
                    SysDepts.dept_id == dept_id,
                    SysDepts.delete_time.is_(None)
                ).first()

                if not existing:
                    return False, f"部门(ID={dept_id})不存在", None

                # 检查同级部门下是否有重名
                if data.get('deptName') and data['deptName'] != existing.dept_name:
                    conflict = session.query(SysDepts).filter(
                        SysDepts.dept_name == data['deptName'],
                        SysDepts.parent_id == (data.get('parentId') or existing.parent_id),
                        SysDepts.dept_id != dept_id,
                        SysDepts.delete_time.is_(None)
                    ).first()

                    if conflict:
                        return False, "同级部门下已存在相同名称", None

                # 更新字段
                update_fields = {
                    'parent_id': data.get('parentId'),
                    'dept_path': data.get('deptPath'),
                    'dept_name': data.get('deptName'),
                    'sort': data.get('sort'),
                    'leader': data.get('leader'),
                    'phone': data.get('phone'),
                    'email': data.get('email'),
                    'status': data.get('status'),
                    'update_by': data.get('updateBy'),
                    'update_time': datetime.now()
                }

                for field, value in update_fields.items():
                    if value is not None:
                        setattr(existing, field, value)

                session.commit()
                session.refresh(existing)

                return True, "更新成功", {
                    'deptId': existing.dept_id,
                    'parentId': existing.parent_id,
                    'deptPath': existing.dept_path,
                    'deptName': existing.dept_name,
                    'sort': existing.sort,
                    'leader': existing.leader,
                    'phone': existing.phone,
                    'email': existing.email,
                    'status': existing.status,
                    'createBy': existing.create_by,
                    'updateBy': existing.update_by,
                    'create_time': existing.create_time.strftime('%Y-%m-%dT%H:%M:%S') if existing.create_time else None,
                    'update_time': existing.update_time.strftime('%Y-%m-%dT%H:%M:%S') if existing.update_time else None
                }

            except Exception as e:
                session.rollback()
                return False, f"更新失败: {str(e)}", None

    @staticmethod
    def delete_dept(dept_id: int) -> Tuple[bool, str]:
        """
        软删除部门

        Args:
            dept_id: 部门ID

        Returns:
            (是否成功, 消息)
        """
        with Session(engine) as session:
            try:
                # 检查是否有子部门
                has_children = session.query(SysDepts).filter(
                    SysDepts.parent_id == dept_id,
                    SysDepts.delete_time.is_(None)
                ).first()

                if has_children:
                    return False, "请先删除子部门"

                dept = session.query(SysDepts).filter(
                    SysDepts.dept_id == dept_id,
                    SysDepts.delete_time.is_(None)
                ).first()

                if not dept:
                    return False, f"部门(ID={dept_id})不存在"

                dept.delete_time = datetime.now()
                session.commit()

                return True, "删除成功"

            except Exception as e:
                session.rollback()
                return False, f"删除失败: {str(e)}"