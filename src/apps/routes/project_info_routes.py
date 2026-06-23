from logging import getLogger

from flask import request

from apps import DDetBlueprint
from apps.schemas.common import CommonResponse, PageResponse
from apps.schemas.project_info_vm import ProjectInfoResp
from db.models.project_info import ProjectInfo
from db.services.project_info_service import ProjectInfoService

logger = getLogger(__name__)

project_info_bp = DDetBlueprint('project_info', __name__, url_prefix='/ProjectInfo')


@project_info_bp.route('/list', methods=['GET'])
def list_project_info():
    page_num = request.args.get('pageNum', default=1, type=int)
    page_size = request.args.get('pageSize', default=10, type=int)

    req_data = {}
    for key in ('prjName', 'prjCode', 'manager', 'prjStatus'):
        value = request.args.get(key, default=None, type=str)
        if value and value.strip():
            req_data[key] = value.strip()

    total, result = ProjectInfoService.list_project_info(req_data, page_num, page_size)
    model_results = [ProjectInfoResp.model_validate(item) for item in result]
    return PageResponse.success(total=total, page_num=page_num, page_size=page_size, data_list=model_results)


@project_info_bp.route('/add', methods=['POST'])
def add_project_info():
    data = request.get_json()
    req = ProjectInfoResp.model_validate(data)
    project_info = ProjectInfo(**req.model_dump(exclude_unset=True))
    ProjectInfoService.add(project_info)
    return CommonResponse.success(message="1")


@project_info_bp.route('/update', methods=['POST'])
def update_project_info():
    data = request.get_json()
    if not data or 'id' not in data:
        return CommonResponse.fail(message="请求体必须包含 id 字段")

    req = ProjectInfoResp.model_validate(data)
    project_info = ProjectInfo(**req.model_dump(exclude_unset=True))
    result = ProjectInfoService.update(project_info)
    if not result:
        return CommonResponse.fail(message=f"ProjectInfo(id={project_info.id}) 不存在")

    return CommonResponse.success(message="1")


@project_info_bp.route('/delete', methods=['POST'])
def delete_project_info():
    data = request.get_json()
    if not data:
        return CommonResponse.fail(message="请求体不能为空")

    if isinstance(data, (int, str)):
        try:
            id_list = [int(data)]
        except (ValueError, TypeError):
            return CommonResponse.fail(message="格式错误，必须是整数或整数数组")
    elif isinstance(data, list):
        id_list = data
    else:
        return CommonResponse.fail(message="必须是整数或整数数组")

    deleted_count = 0
    for project_id in id_list:
        if ProjectInfoService.delete(int(project_id)):
            deleted_count += 1

    logger.info(f"Deleted {deleted_count}/{len(id_list)} ProjectInfo records")
    return CommonResponse.success(data=deleted_count, message="1")
