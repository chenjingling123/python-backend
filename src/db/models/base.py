"""
本文件定义了数据库模型的基础类。
"""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    所有数据库模型的基础类
    提供通用的 to_dict 方法
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典

        Returns:
            包含所有字段的字典，datetime 字段会格式化为字符串
        """
        result = {}
        for attr in self.__mapper__.attrs:
            key = attr.key  # 类属性名
            value = getattr(self, key)

            # 处理 datetime 类型
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")

            result[key] = value

        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典更新模型实例

        Args:
            data: 包含更新数据的字典
        """
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)