"""
此文件定义了 系统菜单 相关的数据模型。
"""
from apps.schemas.common import *

class SysMenusReq(BaseModel):
    MenuId: Optional[int] = Field(default=None, description="唯一标识符")
    MenuName: Optional[str] = Field(default=None, description="菜单名称")
    Status: Optional[str] = Field(default=None, description="菜单状态")


class SysMenusResp(BaseResponse):
    """
    系统菜单响应模型
    """
    menuId: Optional[int] = Field(default=None, alias='menu_id', description="菜单ID")
    menuName: Optional[str] = Field(default=None, alias='menu_name', description="菜单名称")
    title: Optional[str] = Field(default=None, alias='title', description="菜单标题")
    parentId: Optional[int] = Field(default=None, alias='parent_id', description="父菜单ID")
    sort: Optional[int] = Field(default=None, alias='sort', description="排序号")
    icon: Optional[str] = Field(default=None, alias='icon', description="菜单图标")
    path: Optional[str] = Field(default=None, alias='path', description="路由地址")
    component: Optional[str] = Field(default=None, alias='component', description="组件路径")
    isFrame: Optional[str] = Field(default=None, alias='is_frame', description="是否为外链（0是 1否）")
    isLink: Optional[str] = Field(default=None, alias='is_link', description="链接地址")
    menuType: Optional[str] = Field(default=None, alias='menu_type', description="菜单类型（M目录 C菜单 F按钮）")
    isHide: Optional[str] = Field(default=None, alias='is_hide', description="是否隐藏（0显示 1隐藏）")
    isKeepAlive: Optional[str] = Field(default=None, alias='is_keep_alive', description="是否缓存（0缓存 1不缓存）")
    isAffix: Optional[str] = Field(default=None, alias='is_affix', description="是否固定在页面顶部（0否 1是）")
    permission: Optional[str] = Field(default=None, alias='permission', description="权限标识")
    status: Optional[str] = Field(default=None, alias='status', description="状态（0正常 1停用）")
    createBy: Optional[str] = Field(default=None, alias='create_by', description="创建者")
    update_by: Optional[str] = Field(default=None, alias='update_by', description="更新者")
    remark: Optional[str] = Field(default=None, alias='remark', description="备注")
    create_time: Optional[datetime] = Field(default=None, alias='create_time', description="创建时间")
    update_time: Optional[datetime] = Field(default=None, alias='update_time', description="更新时间")
    children: Optional[List['SysMenusResp']] = Field(default_factory=list, alias='children', description="子菜单列表")

    #下面这个这里必须要有：允许使用字段名填充，否则返回的很多字段为null
    model_config = {
        "populate_by_name": True
    }