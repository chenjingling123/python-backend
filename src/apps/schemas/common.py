"""
文件定义了通用的响应数据模型 CommonResponse 和 BaseResponse。
"""

from typing import Generic, Optional, TypeVar, Union, List
from datetime import datetime
import json
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, ValidationInfo

T = TypeVar('T')

class CommonResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="响应码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[Union[T, str, dict, list]] = Field(default=None, description="返回的数据体")

    @classmethod
    def success(cls, data: Optional[Union[T, str, dict, list]] = None, message: str = "success") -> str:
        """成功响应"""
        return cls(code=200, msg=message, data=data).model_dump_json()

    @classmethod
    def fail(cls, code: int = 400, message: str = "error") -> str:
        """失败响应"""
        return cls(code=code, msg=message, data=None).model_dump_json()

class PageData(BaseModel, Generic[T]):
    """分页数据内部结构"""
    data: List[T] = Field(default_factory=list, description="当前页数据")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页记录数")
    pageNum: int = Field(default=1, ge=1, description="当前页码")
    total: int = Field(default=0, description="总记录数")

class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(default=200, description="响应码")
    msg: str = Field(default="success", description="响应消息")
    data: Optional[PageData[T]] = Field(default=None, description="分页数据")

    @classmethod
    def success(cls, total: int, page_num: int, page_size: int, data_list: List[T]) -> str:
        """
        成功响应 - 返回指定格式的分页数据

        Args:
            total: 总记录数
            page_num: 当前页码
            page_size: 每页记录数
            data_list: 当前页数据列表

        Returns:
            JSON字符串，格式为:
            {
                "code": 200,
                "msg": "success",
                "data": {
                    "data": [...],
                    "pageSize": 10,
                    "pageNum": 1,
                    "total": 100
                }
            }
        """
        page_data = PageData[T](
            data=data_list,
            pageSize=page_size,
            pageNum=page_num,
            total=total
        )
        return cls(code=200, msg="success", data=page_data).model_dump_json()

    @classmethod
    def error(cls, code: int, message: str) -> str:
        """
        错误响应
        """
        return cls(code=code, msg=message, data=None).model_dump_json()

class PageResponseData(BaseModel, Generic[T]):
    page_num: int = Field(default=1)
    page_size: int = Field(default=10)
    total: int = Field(default=0)
    rows: Optional[List[T]] = None

    @classmethod
    def build(cls, rows: list, page_num: int, page_size: int, total: int):
        return cls(page_num=page_num, page_size=page_size, total=total, rows=rows)



class PageRequest(BaseModel, Generic[T]):
    """分页请求模型（带排序功能）"""
    page_num: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页记录数，最大100")
    data: Optional[T] = Field(default=None, description="查询条件")

    # ✅ 新增排序字段
    order_by: Optional[str] = Field(default="id", description="排序字段名（数据库列名）")
    order_dir: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="排序方向（asc 或 desc）")

class BaseResponse(BaseModel):
    """
    基础响应模型
    
    定义了通用的序列化配置，特别是对 datetime 类型的处理。
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
        }    
    )

#################################
##下面helm 添加，有错误
def sqlalchemy_to_dict(obj):
    """将 SQLAlchemy 对象安全转换为 dict"""
    if obj is None:
        return None
    data = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # datetime 类型转 str
        if hasattr(value, "isoformat"):
            value = str(value)
        data[column.name] = value
    return data



class PageResponse2(BaseModel, Generic[T]):
    code: int = Field(default=200)
    message: str = Field(default="success")
    data: Optional[Union[T, dict, list, str]] = None

    @classmethod
    def success(cls, data=None, message="成功") -> str:
        # data 必须是 dict/list/str，可序列化
        if isinstance(data, BaseModel):
            data = data.model_dump()  # Pydantic 对象可以用 model_dump
        elif hasattr(data, "__dict__") and hasattr(data, "__table__"):  # SQLAlchemy 对象
            data = sqlalchemy_to_dict(data)
        return json.dumps({
            "code": 200,
            "message": message,
            "data": data
        })

    @classmethod
    def build_paginated_response(cls, rows: list, page_num: int, page_size: int, total: int) -> str:
        # 将每一行安全序列化
        rows_serialized = []
        for row in rows:
            if isinstance(row, BaseModel):
                rows_serialized.append(row.model_dump())
            elif hasattr(row, "__dict__") and hasattr(row, "__table__"):  # SQLAlchemy
                rows_serialized.append(sqlalchemy_to_dict(row))
            else:
                rows_serialized.append(row)

        page_data = PageResponseData.build(rows_serialized, page_num, page_size, total)
        return cls.success(data=page_data)


