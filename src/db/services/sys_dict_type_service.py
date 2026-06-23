# services/sys_dict_type_service.py
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session

from db.models.sys_dict_type import SysDictType
from db import engine


class SysDictTypeService:
    """系统字典类型服务类"""

    @staticmethod
    def get_table_data(page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        获取字典类型表格数据（对应 C# 的 GetTableData 方法）

        Args:
            page_num: 当前页码
            page_size: 每页记录数

        Returns:
            返回格式：{
                "code": 200,
                "msg": "success",
                "data": {
                    "data": [...],
                    "total": 100,
                    "pageNum": 1,
                    "pageSize": 10
                }
            }
        """
        try:
            with Session(engine) as session:
                # 构建基础查询（只查询未删除的记录）
                query = session.query(SysDictType).filter(SysDictType.delete_time.is_(None))

                # 获取总记录数
                total = query.count()

                # 分页查询并按 DictId 排序（对应 C# 的 r => r.DictId, true）
                # true 表示正序（升序）
                records = query.order_by(SysDictType.dict_id.asc()).offset(
                    (page_num - 1) * page_size
                ).limit(page_size).all()

                # 转换为字典列表（对应 C# 的 _mapper.Map）
                results = [record.to_dict() for record in records]

                # 构建表格数据（对应 C# 的 VueTable）
                table_data = {
                    'data': results,
                    'total': total,
                    'pageNum': page_num,
                    'pageSize': page_size
                }

                # 返回成功响应（对应 C# 的 VueResMsg）
                return {
                    'code': 200,
                    'msg': 'success',
                    'data': table_data
                }

        except Exception as e:
            return {
                'code': 500,
                'msg': f'获取字典类型列表失败: {str(e)}',
                'data': {
                    'data': [],
                    'total': 0,
                    'pageNum': page_num,
                    'pageSize': page_size
                }
            }

    @staticmethod
    def get_table_data_with_filters(
            page_num: int = 1,
            page_size: int = 10,
            dict_name: Optional[str] = None,
            dict_type: Optional[str] = None,
            status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        带过滤条件的字典类型表格数据

        Args:
            page_num: 当前页码
            page_size: 每页记录数
            dict_name: 字典名称（模糊查询）
            dict_type: 字典类型（模糊查询）
            status: 状态

        Returns:
            表格数据
        """
        try:
            with Session(engine) as session:
                # 基础查询
                query = session.query(SysDictType).filter(SysDictType.delete_time.is_(None))

                # 添加过滤条件
                filters = []

                if dict_name:
                    filters.append(SysDictType.dict_name.like(f'%{dict_name}%'))
                if dict_type:
                    filters.append(SysDictType.dict_type.like(f'%{dict_type}%'))
                if status:
                    filters.append(SysDictType.status == status)

                if filters:
                    query = query.filter(and_(*filters))

                # 获取总记录数
                total = query.count()

                # 分页查询
                records = query.order_by(SysDictType.dict_id.asc()).offset(
                    (page_num - 1) * page_size
                ).limit(page_size).all()

                # 转换为字典列表
                results = [record.to_dict() for record in records]

                return {
                    'code': 200,
                    'msg': 'success',
                    'data': {
                        'data': results,
                        'total': total,
                        'pageNum': page_num,
                        'pageSize': page_size
                    }
                }

        except Exception as e:
            return {
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': {
                    'data': [],
                    'total': 0,
                    'pageNum': page_num,
                    'pageSize': page_size
                }
            }

    @staticmethod
    def get_dict_type_by_id(dict_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取字典类型（对应单个查询）

        Args:
            dict_id: 字典ID

        Returns:
            字典类型数据或None
        """
        with Session(engine) as session:
            record = session.query(SysDictType).filter(
                SysDictType.dict_id == dict_id,
                SysDictType.delete_time.is_(None)
            ).first()

            return record.to_dict() if record else None

    @staticmethod
    def get_dict_type_by_type(dict_type: str) -> Optional[Dict[str, Any]]:
        """
        根据字典类型编码获取字典类型

        Args:
            dict_type: 字典类型编码

        Returns:
            字典类型数据或None
        """
        with Session(engine) as session:
            record = session.query(SysDictType).filter(
                SysDictType.dict_type == dict_type,
                SysDictType.delete_time.is_(None)
            ).first()

            return record.to_dict() if record else None

    @staticmethod
    def add_dict_type(data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        添加字典类型（对应新增操作）

        Args:
            data: 字典类型数据

        Returns:
            (是否成功, 消息, 数据)
        """
        with Session(engine) as session:
            try:
                # 检查字典类型是否已存在
                existing = session.query(SysDictType).filter(
                    SysDictType.dict_type == data.get('dictType'),
                    SysDictType.delete_time.is_(None)
                ).first()

                if existing:
                    return False, "字典类型已存在", None

                # 创建新记录
                new_type = SysDictType(
                    dict_name=data.get('dictName'),
                    dict_type=data.get('dictType'),
                    status=data.get('status', '0'),
                    remark=data.get('remark'),
                    create_by=data.get('createBy'),
                    create_time=datetime.now()
                )

                session.add(new_type)
                session.commit()
                session.refresh(new_type)

                return True, "添加成功", new_type.to_dict()

            except Exception as e:
                session.rollback()
                return False, f"添加失败: {str(e)}", None

    @staticmethod
    def update_dict_type(dict_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        更新字典类型（对应编辑操作）

        Args:
            dict_id: 字典ID
            data: 要更新的数据

        Returns:
            (是否成功, 消息, 数据)
        """
        with Session(engine) as session:
            try:
                existing = session.query(SysDictType).filter(
                    SysDictType.dict_id == dict_id,
                    SysDictType.delete_time.is_(None)
                ).first()

                if not existing:
                    return False, f"字典类型(ID={dict_id})不存在", None

                # 如果修改了字典类型编码，检查是否与其他记录冲突
                if data.get('dictType') and data['dictType'] != existing.dict_type:
                    conflict = session.query(SysDictType).filter(
                        SysDictType.dict_type == data['dictType'],
                        SysDictType.dict_id != dict_id,
                        SysDictType.delete_time.is_(None)
                    ).first()

                    if conflict:
                        return False, "字典类型已存在", None

                # 更新字段
                update_fields = {
                    'dict_name': data.get('dictName'),
                    'dict_type': data.get('dictType'),
                    'status': data.get('status'),
                    'remark': data.get('remark'),
                    'update_by': data.get('updateBy'),
                    'update_time': datetime.now()
                }

                for field, value in update_fields.items():
                    if value is not None:
                        setattr(existing, field, value)

                session.commit()
                session.refresh(existing)

                return True, "更新成功", existing.to_dict()

            except Exception as e:
                session.rollback()
                return False, f"更新失败: {str(e)}", None

    @staticmethod
    def delete_dict_type(dict_id: int) -> Tuple[bool, str]:
        """
        软删除字典类型（对应删除操作）

        Args:
            dict_id: 字典ID

        Returns:
            (是否成功, 消息)
        """
        with Session(engine) as session:
            try:
                type_obj = session.query(SysDictType).filter(
                    SysDictType.dict_id == dict_id,
                    SysDictType.delete_time.is_(None)
                ).first()

                if not type_obj:
                    return False, f"字典类型(ID={dict_id})不存在"

                type_obj.delete_time = datetime.now()
                session.commit()

                return True, "删除成功"

            except Exception as e:
                session.rollback()
                return False, f"删除失败: {str(e)}"

    @staticmethod
    def batch_delete_dict_type(dict_ids: List[int]) -> Tuple[int, str]:
        """
        批量删除字典类型

        Args:
            dict_ids: 字典ID列表

        Returns:
            (成功删除数量, 消息)
        """
        with Session(engine) as session:
            try:
                success_count = 0
                for dict_id in dict_ids:
                    type_obj = session.query(SysDictType).filter(
                        SysDictType.dict_id == dict_id,
                        SysDictType.delete_time.is_(None)
                    ).first()

                    if type_obj:
                        type_obj.delete_time = datetime.now()
                        success_count += 1

                session.commit()
                return success_count, f"成功删除{success_count}条记录"

            except Exception as e:
                session.rollback()
                return 0, f"批量删除失败: {str(e)}"