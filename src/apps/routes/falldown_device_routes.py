from logging import getLogger

from flask import request

# 注意这里要导入自定义的 DDetBlueprint，而不是导入 Blueprint
from apps import DDetBlueprint
from apps.schemas.common import CommonResponse, PageResponse
from apps.schemas.falldown_device_vm import FalldownDeviceResp
from db.services.falldown_device_service import FalldownDeviceService
from db.models.falldown_device import FalldownDevice

logger = getLogger(__name__)

falldown_device_bp = DDetBlueprint('falldown_device', __name__, url_prefix='/device/falldowndevice')

@falldown_device_bp.route('/list', methods=['GET'])
def list_falldown_device():

    # 获取查询参数（从URL查询字符串中）
    pageNum = request.args.get('pageNum', default=1, type=int)
    pageSize = request.args.get('pageSize', default=10, type=int)

    #其他的请求参数
    DeviceCode = request.args.get('DeviceCode', default=None, type=str)
    Model = request.args.get('Model', default=None, type=str)
    Status = request.args.get('Status', default=None, type=str)
    # 组装查询条件字典（只添加非空的查询条件）
    reqData = {}
    if DeviceCode and DeviceCode.strip():
        reqData['DeviceCode'] = DeviceCode.strip()

    if Model and Model.strip():
        reqData['Model'] = Model.strip()

    if Status and Status.strip():
        reqData['Status'] = Status.strip()
    # 打印调试信息
    logger.debug(f"查询条件: {reqData}, 分页参数: pageNum={pageNum}, pageSize={pageSize}")

    total, result = FalldownDeviceService.list_falldown_device(
        reqData,
        pageNum,
        pageSize
    )

    model_results = [FalldownDeviceResp.model_validate(item) for item in result]
    logger.debug(f'Fetched FalldownDevice: {model_results}')
    return PageResponse.success(total=total,page_num=pageNum,page_size=pageSize, data_list=model_results)

# 新增接口
@falldown_device_bp.route('/add', methods=['POST'])
def add_falldown_device():
    try:
        # 1️⃣ 从请求中解析 JSON 并转成 Pydantic 模型
        data = request.get_json()
        req = FalldownDeviceResp.model_validate(data)
        logger.debug(f"Received FalldownDevice data: {req}")

        # 2️⃣ 将 Pydantic 模型转换成 SQLAlchemy 模型实例        
        falldown_device_db = FalldownDevice(**req.model_dump(exclude_unset=True))

        # 3️⃣ 调用 service 层写入数据库
        added_model = FalldownDeviceService.add(falldown_device_db)

        # 4️⃣ 返回新增后的对象（包括数据库生成的 ID）
        resp = FalldownDeviceResp.model_validate(added_model)

        return CommonResponse.success(resp)

    except Exception as e:
        logger.exception("Error adding falldown_device")
        return CommonResponse.fail(message=str(e))

#更新接口
@falldown_device_bp.route('/update', methods=['POST'])
def update_falldown_device():
    """更新模型信息"""
    data = request.get_json()
    if not data or 'Id' not in data:
        return CommonResponse.fail(message="请求体必须包含 id 字段")

    model_data = FalldownDeviceResp.model_validate(data)
    model = FalldownDevice(**model_data.model_dump(exclude_unset=True))

    result = FalldownDeviceService.update(model)
    if not result:
        return CommonResponse.fail(message=f"FalldownDevice(id={model.Id}) 不存在")

    logger.info(f"Updated ModelInfo: {result.Id}")
    return CommonResponse.success(FalldownDeviceResp.model_validate(result))


#批量删除接口
@falldown_device_bp.route('/delete', methods=['POST'])
def delete_falldown_device():
    """批量删除跌倒设备信息"""
    data = request.get_json()

    # 处理没有请求体的情况
    if not data:
        return CommonResponse.fail(message="请求体不能为空")

    # 统一转换为列表处理
    id_list = []

    # 判断 ids 的类型
    if isinstance(data, (int, str)):  # 单个ID（整数或数字字符串）
        try:
            id_list = [int(data)]
        except (ValueError, TypeError):
            return CommonResponse.fail(message="格式错误，必须是整数或整数数组")

    elif isinstance(data, list):  # ID数组
        id_list = data
    else:
        return CommonResponse.fail(message="必须是整数或整数数组")

    # 检查是否有有效的ID
    if not id_list:
        return CommonResponse.fail(message="没有有效的ID可删除")

    # 执行批量删除
    deleted_count = 0
    failed_ids = []

    for mid in id_list:
        if FalldownDeviceService.delete(mid):  # 注意这里的方法名可能需要调整
            deleted_count += 1
        else:
            failed_ids.append(mid)

    # 记录日志
    logger.info(f"Deleted {deleted_count}/{len(id_list)} FalldownDevice records")
    if failed_ids:
        logger.warning(f"Failed to delete IDs: {failed_ids}")

    # 返回响应
    return CommonResponse.success(
        data={
            "deletedCount": deleted_count,
            "failedIds": failed_ids,
            "totalIds": len(id_list)
        },
        message=f"成功删除 {deleted_count} 条记录"
    )