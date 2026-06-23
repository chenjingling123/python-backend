# services/sys_dict_data_service.py
from typing import Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models.sys_dict_data import SysDictData
from db import engine


class SysDictDataService:
    """系统字典数据服务类"""

    @staticmethod
    def get_dicts(dict_type: str) -> Dict[str, Any]:
        """
        根据字典类型获取字典数据（对应 C# 的 GetDicts 方法）

        Args:
            dict_type: 字典类型，例如 "sys_user_sex"

        Returns:
            返回格式：{"code": 200, "msg": "success", "data": [...]}
        """
        try:
            with Session(engine) as session:
                # 构建查询条件（对应 C# 的 PredicateExtensions）
                query = session.query(SysDictData).filter(
                    SysDictData.delete_time.is_(None)  # 只查询未删除的数据
                )

                # 添加字典类型条件（不区分大小写）
                if dict_type:
                    query = query.filter(
                        func.upper(SysDictData.dict_type) == dict_type.upper()
                    )

                # 执行查询并按 dict_code 排序（对应 C# 的 r => r.DictCode, true）
                records = query.order_by(SysDictData.dict_code).all()

                # 转换为字典列表（对应 C# 的 _mapper.Map）
                results = [record.to_dict() for record in records]

                # 返回成功响应（对应 C# 的 VueResMsg<List<SysDictDatumModel>>）
                return {
                    'code': 200,
                    'msg': 'success',
                    'data': results
                }

        except Exception as e:
            return {
                'code': 500,
                'msg': f'获取字典数据失败: {str(e)}',
                'data': []
            }