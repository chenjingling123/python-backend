"""
此文件定义了 系统岗位 相关的数据模型。
"""
from apps.schemas.common import *

class SysPostsResp(BaseResponse):
    """
    系统岗位响应模型
    """
    postId: Optional[int] = Field(default=None, alias='post_id', description="岗位ID")
    postName: Optional[str] = Field(default=None, alias='post_name', description="岗位名称")
    postCode: Optional[str] = Field(default=None, alias='post_code', description="岗位代码")
    sort: Optional[int] = Field(default=None, alias='sort', description="排序号")
    status: Optional[str] = Field(default=None, alias='status', description="状态")
    createBy: Optional[str] = Field(default=None, alias='create_by', description="创建者")
    update_by: Optional[str] = Field(default=None, alias='update_by', description="更新者")
    remark: Optional[str] = Field(default=None, alias='remark', description="备注")
    create_time: Optional[datetime] = Field(default=None, alias='create_time', description="创建时间")
    update_time: Optional[datetime] = Field(default=None, alias='update_time', description="更新时间")

    