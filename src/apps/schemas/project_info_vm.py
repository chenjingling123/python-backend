from decimal import Decimal

from apps.schemas.common import *
from pydantic import field_serializer


class ProjectInfoResp(BaseResponse):
    id: Optional[int] = Field(default=None, description="项目ID")
    prjName: Optional[str] = Field(default=None, description="项目名称")
    prjCode: Optional[str] = Field(default=None, description="项目编号")
    prjType: Optional[int] = Field(default=None, description="项目类型")
    prjStatus: Optional[str] = Field(default=None, description="项目状态")
    prjDesc: Optional[str] = Field(default=None, description="项目描述")
    startDate: Optional[datetime] = Field(default=None, description="开始时间")
    endDate: Optional[datetime] = Field(default=None, description="结束时间")
    manager: Optional[str] = Field(default=None, description="项目经理")
    money: Optional[Decimal] = Field(default=None, description="金额")
    remark: Optional[str] = Field(default=None, description="备注")
    createBy: Optional[str] = Field(default=None, description="创建人")
    updateBy: Optional[str] = Field(default=None, description="更新人")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")

    @field_serializer('money')
    def serialize_money(self, money: Optional[Decimal]):
        return float(money) if money is not None else None
