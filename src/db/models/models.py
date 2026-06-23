"""
本文件定义了数据库模型和数据表结构。
"""
from typing import List

class DeptSelect:
    """
    部门选择数据类，对应 C# 的 deptsSelect
    """

    def __init__(self, checked_keys: List[int] = None, depts: List[dict] = None):
        self.checkedKeys = checked_keys or []  # 选中的部门ID列表
        self.depts = depts or []  # 部门树列表

    def to_dict(self) -> dict:
        """
        转换为字典格式
        """
        return {
            'checkedKeys': self.checkedKeys,
            'depts': self.depts
        }

