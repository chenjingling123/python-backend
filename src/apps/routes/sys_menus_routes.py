# routes/dept_routes.py
from logging import getLogger
from flask import request, jsonify
from datetime import datetime
from apps.schemas.common import CommonResponse
from apps.schemas.sys_menus_vm import SysMenusResp
from apps import DDetBlueprint
from db.models.sys_menus import SysMenus
from db.services.sys_menus_service import SysMenusService

logger = getLogger(__name__)

# 创建蓝图，对应 C# 的 DeptController
menu_bp = DDetBlueprint('sys_menus', __name__, url_prefix='/system/menu')

#from utils.common import parse_int_param, parse_str_param, handle_sqlalchemy_error

@menu_bp.route('/list', methods=['GET'])
def get_menu_list():
    """
    获取菜单列表（树结构）
    """
    menu_name = request.args.get('menuName')
    status = request.args.get('status')

    menus = SysMenusService.get_menu_list(
        menu_name=menu_name,
        status=status
    )

    # ✅ 第一步：构建树（用我们之前写的函数）
    tree = SysMenusService.build_frontend_menu_tree(menus)

    # ✅ 第二步：dict → Pydantic（关键：递归）
    def convert_to_pydantic(data_list):
        result = []
        for item in data_list:
            children = item.pop("children", None)

            obj = SysMenusResp(**item)

            # 递归 children
            if children:
                obj.children = convert_to_pydantic(children)
            else:
                obj.children = None   # ⚠️ 关键：你要求是 null

            result.append(obj)
        return result

    model_results = convert_to_pydantic(tree)

    return CommonResponse.success(data=model_results)

@menu_bp.route('/list2', methods=['GET'])
def get_menu_list2():
    """
    获取菜单列表
    对应C#接口: GET /system/menu/list
    """
    try:
        # 获取查询参数
        """
        data = request.get_json()
        menu_name = data.get('menuName')
        status = data.get('status')
         """
        # 获取查询参数（从URL查询字符串中）
        menu_name = request.args.get('menuName')
        status = request.args.get('status')

        # 调用服务层获取菜单列表
        menus = SysMenusService.get_menu_list(
            menu_name=menu_name,
            status=status
        )

        # 转换为字典列表
        menu_list = SysMenusService.menus_to_dict_list(menus)

        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': menu_list
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@menu_bp.route('/treeselect', methods=['GET'])
def get_menu_tree_select():
    """
    获取菜单树选择器数据
    对应C#接口: GET /system/menu/treeselect
    """
    try:
        # 获取所有菜单
        menus = SysMenusService.get_all_menus()

        # 构建树形结构
        menu_tree = SysMenusService.build_menu_tree(menus)

        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': menu_tree
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@menu_bp.route('/roleMenuTreeselect/<int:role_id>', methods=['GET'])
def get_role_menu_tree_select(role_id):
    """
    根据角色ID获取菜单树选择器数据
    对应C#接口: GET /system/menu/roleMenuTreeselect/{roleId}
    """
    try:
        # 获取所有菜单树
        menus = SysMenusService.get_all_menus()
        menu_tree = SysMenusService.build_menu_tree(menus)

        # 获取角色已分配的菜单ID
        checked_keys = SysMenusService.get_menu_ids_by_role_id(role_id)

        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': {
                'menus': menu_tree,
                'checkedKeys': checked_keys
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@menu_bp.route('/<int:menu_id>', methods=['GET'])
def get_menu_detail(menu_id):
    """
    获取菜单详情
    对应C#接口: GET /system/menu/{menuId}
    """
    try:
        menu = SysMenusService.get_menu_by_id(menu_id)

        if not menu:
            return jsonify({
                'code': 404,
                'msg': '菜单不存在',
                'data': None
            })

        return jsonify({
            'code': 200,
            'msg': 'success',
            'data': menu.to_dict() if menu else None
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@menu_bp.route('', methods=['POST'])
def add_menu():
    """
    新增菜单
    对应C#接口: POST /system/menu
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空',
                'data': None
            })

        # 参数验证
        if not data.get('menuName'):
            return jsonify({
                'code': 400,
                'msg': '菜单名称不能为空',
                'data': None
            })

        # 创建菜单对象
        menu_data = {
            'menu_name': data.get('menuName'),
            'title': data.get('title'),
            'parent_id': data.get('parentId', 0),
            'sort': data.get('sort', 0),
            'icon': data.get('icon'),
            'path': data.get('path'),
            'component': data.get('component'),
            'is_frame': data.get('isFrame', '0'),
            'is_link': data.get('isLink'),
            'menu_type': data.get('menuType'),
            'is_hide': data.get('isHide', '0'),
            'is_keep_alive': data.get('isKeepAlive', '0'),
            'is_affix': data.get('isAffix', '0'),
            'permission': data.get('permission'),
            'status': data.get('status', '0'),
            'remark': data.get('remark'),
            'create_by': data.get('createBy', 'system'),
            'create_time': datetime.now()
        }

        menu = SysMenus.from_dict(menu_data)

        # 保存到数据库
        success, result = SysMenusService.add_menu(menu)

        if success:
            return jsonify({
                'code': 200,
                'msg': '新增成功',
                'data': result.to_dict() if result else None
            })
        else:
            return jsonify({
                'code': 500,
                'msg': result,
                'data': None
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'新增失败: {str(e)}',
            'data': None
        })


@menu_bp.route('', methods=['PUT'])
def update_menu():
    """
    修改菜单
    对应C#接口: PUT /system/menu
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空',
                'data': None
            })

        menu_id = data.get('menuId')
        if not menu_id:
            return jsonify({
                'code': 400,
                'msg': '菜单ID不能为空',
                'data': None
            })

        # 检查菜单是否存在
        existing_menu = SysMenusService.get_menu_by_id(menu_id)
        if not existing_menu:
            return jsonify({
                'code': 404,
                'msg': '菜单不存在',
                'data': None
            })

        # 更新数据
        update_data = {
            'menu_name': data.get('menuName'),
            'title': data.get('title'),
            'parent_id': data.get('parentId'),
            'sort': data.get('sort'),
            'icon': data.get('icon'),
            'path': data.get('path'),
            'component': data.get('component'),
            'is_frame': data.get('isFrame'),
            'is_link': data.get('isLink'),
            'menu_type': data.get('menuType'),
            'is_hide': data.get('isHide'),
            'is_keep_alive': data.get('isKeepAlive'),
            'is_affix': data.get('isAffix'),
            'permission': data.get('permission'),
            'status': data.get('status'),
            'remark': data.get('remark'),
            'update_by': data.get('updateBy', 'system'),
            'update_time': datetime.now()
        }

        # 过滤掉None值
        update_data = {k: v for k, v in update_data.items() if v is not None}

        success, result = SysMenusService.update_menu(menu_id, update_data)

        if success:
            return jsonify({
                'code': 200,
                'msg': '更新成功',
                'data': result.to_dict() if result else None
            })
        else:
            return jsonify({
                'code': 500,
                'msg': result,
                'data': None
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'更新失败: {str(e)}',
            'data': None
        })


@menu_bp.route('/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    """
    删除菜单
    对应C#接口: DELETE /system/menu/{menuId}
    """
    try:
        # 检查是否有子菜单
        has_children = SysMenusService.has_child_menus(menu_id)
        if has_children:
            return jsonify({
                'code': 400,
                'msg': '存在子菜单，不允许删除',
                'data': None
            })

        # 检查是否已分配给角色
        is_assigned = SysMenusService.is_menu_assigned_to_role(menu_id)
        if is_assigned:
            return jsonify({
                'code': 400,
                'msg': '菜单已分配给角色，不能删除',
                'data': None
            })

        # 执行删除（软删除）
        success, result = SysMenusService.delete_menu(menu_id)

        if success:
            return jsonify({
                'code': 200,
                'msg': '删除成功',
                'data': None
            })
        else:
            return jsonify({
                'code': 500,
                'msg': result,
                'data': None
            })

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'删除失败: {str(e)}',
            'data': None
        })

