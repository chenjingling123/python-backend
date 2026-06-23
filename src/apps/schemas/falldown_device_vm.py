"""
此文件定义了 系统岗位 相关的数据模型。
"""
from apps.schemas.common import *

class FalldownDeviceResp(BaseResponse):
    """
    跌倒设备响应模型
    """
    Id: Optional[int] = Field(default=None, alias='Id', description="设备ID")
    DeviceCode: Optional[str] = Field(default=None, alias='DeviceCode', description="设备编码")
    Status: Optional[str] = Field(default=None, alias='Status', description="状态")
    Model: Optional[str] = Field(default=None, alias='Model', description="型号")
    ContactPhones: Optional[str] = Field(default=None, alias='ContactPhones', description="家属电话")
    Phone: Optional[str] = Field(default=None, alias='Phone', description="电话")
    Flag: Optional[str] = Field(default=None, alias='Flag', description="删除标识")
    CreateBy: Optional[str] = Field(default=None, alias='CreateBy', description="创建者")
    CreateTime: Optional[datetime] = Field(default=None, alias='CreateTime', description="创建时间")
    UpdateBy: Optional[str] = Field(default=None, alias='UpdateBy', description="更新者")
    UpdateTime: Optional[datetime] = Field(default=None, alias='UpdateTime', description="更新时间")
    DeleteTime: Optional[datetime] = Field(default=None, alias='DeleteTime', description="删除时间")
    Remark: Optional[str] = Field(default=None, alias='Remark', description="备注")

    