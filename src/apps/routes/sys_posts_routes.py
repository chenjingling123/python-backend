from logging import getLogger

from flask import request

# 注意这里要导入自定义的 DDetBlueprint，而不是导入 Blueprint
from apps import DDetBlueprint
from apps.schemas.common import CommonResponse, PageResponse
from apps.schemas.sys_posts_vm import SysPostsResp
from db.services.sys_posts_service import SysPostsService
from db.models.sys_posts import SysPosts

logger = getLogger(__name__)

sys_posts_bp = DDetBlueprint('sys_posts', __name__, url_prefix='/system/post')

@sys_posts_bp.route('/list', methods=['GET'])
def list_sys_posts():

    # 获取查询参数（从URL查询字符串中）
    pageNum = request.args.get('pageNum', default=1, type=int)
    pageSize = request.args.get('pageSize', default=10, type=int)

    #其他的请求参数？
    reqData = None

    total, result = SysPostsService.list_sys_posts(
        reqData,
        pageNum,
        pageSize
    )

    model_results = [SysPostsResp.model_validate(item) for item in result]
    logger.debug(f'Fetched SysPosts: {model_results}')
    return PageResponse.success(total=total,page_num=pageNum,page_size=pageSize, data_list=model_results)

# 新增接口
@sys_posts_bp.route('/add', methods=['POST'])
def add_sys_posts():
    try:
        # 1️⃣ 从请求中解析 JSON 并转成 Pydantic 模型
        data = request.get_json()
        model_info_req = SysPostsResp.model_validate(data)
        logger.debug(f"Received ModelInfo data: {model_info_req}")

        # 2️⃣ 将 Pydantic 模型转换成 SQLAlchemy 模型实例        
        model_info_db = SysPosts(**model_info_req.model_dump(exclude_unset=True))

        # 3️⃣ 调用 service 层写入数据库
        added_model = SysPostsService.add_model_info(model_info_db)

        # 4️⃣ 返回新增后的对象（包括数据库生成的 ID）
        model_info_resp = SysPostsResp.model_validate(added_model)

        return CommonResponse.success(model_info_resp)

    except Exception as e:
        logger.exception("Error adding model info")
        return CommonResponse.fail(message=str(e))

#更新接口
@sys_posts_bp.route('/update', methods=['POST'])
def update_sys_posts():
    """更新模型信息"""
    data = request.get_json()
    if not data or 'id' not in data:
        return CommonResponse.fail(message="请求体必须包含 id 字段")

    model_data = SysPostsResp.model_validate(data)
    model = SysPosts(**model_data.model_dump(exclude_unset=True))

    result = SysPostsService.update_sys_post(model)
    if not result:
        return CommonResponse.fail(message=f"ModelInfo(id={model.id}) 不存在")

    logger.info(f"Updated ModelInfo: {result.id}")
    return CommonResponse.success(SysPostsResp.model_validate(result))


#批量删除接口
@sys_posts_bp.route('/delete', methods=['POST'])
def delete_sys_posts():
    """批量删除模型信息"""
    data = request.get_json()
    if not data or 'ids' not in data or not isinstance(data['ids'], list):
        return CommonResponse.fail(message="请求体必须包含 ids 数组")

    deleted_count = 0
    for mid in data['ids']:
        if SysPostsService.delete_model_info(mid):
            deleted_count += 1

    logger.info(f"Deleted {deleted_count}/{len(data['ids'])} ModelInfo records")
    return CommonResponse.success(data=f"{deleted_count}",message=f"成功删除 {deleted_count} 条记录")
