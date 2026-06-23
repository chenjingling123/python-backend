# routes/dept_routes.py
from flask import request, jsonify
from typing import Optional

from apps import DDetBlueprint
from db.services.sys_depts_service import SysDeptsService

# 创建蓝图，对应 C# 的 DeptController
dept_bp = DDetBlueprint('dept', __name__, url_prefix='/system/dept')


@dept_bp.route('/deptTree', methods=['GET'])
def dept_tree():
    """
    获取部门树（对应 C# 的 deptTree 方法）
    返回完整的部门树结构
    """
    try:
        # 调用 service 获取部门树
        result = SysDeptsService.get_dept_tree()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取部门树失败: {str(e)}',
            'data': []
        })


@dept_bp.route('/list', methods=['GET'])
def list_depts():
    """
    获取部门列表/树（对应 C# 的 list 方法）
    返回部门表格数据
    """
    try:
        # 调用 service 获取表格数据
        result = SysDeptsService.get_table_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取部门列表失败: {str(e)}',
            'data': []
        })


@dept_bp.route('/roleDeptTreeSelect', methods=['GET'])
def role_dept_tree_select():
    """
    根据角色ID获取部门树选择数据（对应 C# 的 roleDeptTreeSelect 方法）
    请求参数：
        roleId: 角色ID
    """
    try:
        # 获取角色ID参数
        role_id = request.args.get('roleId', type=int)

        if role_id is None:
            return jsonify({
                'code': 400,
                'msg': '角色ID不能为空',
                'data': {
                    'checkedKeys': [],
                    'depts': []
                }
            })

        # 调用 service 获取角色部门树
        result = SysDeptsService.get_role_dept_tree(role_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'获取角色部门树失败: {str(e)}',
            'data': {
                'checkedKeys': [],
                'depts': []
            }
        })


# 可选：添加额外的部门管理接口
@dept_bp.route('/<int:dept_id>', methods=['GET'])
def get_dept(dept_id: int):
    """根据ID获取部门详情"""
    try:
        dept = SysDeptsService.get_dept_by_id(dept_id)

        if dept:
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': dept
            })
        else:
            return jsonify({
                'code': 404,
                'msg': f'部门(ID={dept_id})不存在',
                'data': None
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@dept_bp.route('/add', methods=['POST'])
def add_dept():
    """添加部门"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空'
            })

        success, message, dept = SysDeptsService.add_dept(data)

        if success:
            return jsonify({
                'code': 200,
                'msg': message,
                'data': dept
            })
        else:
            return jsonify({
                'code': 400,
                'msg': message,
                'data': None
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'添加失败: {str(e)}',
            'data': None
        })


@dept_bp.route('/edit', methods=['PUT'])
def edit_dept():
    """编辑部门"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空'
            })

        dept_id = data.get('deptId')
        if not dept_id:
            return jsonify({
                'code': 400,
                'msg': '部门ID不能为空'
            })

        success, message, dept = SysDeptsService.update_dept(dept_id, data)

        if success:
            return jsonify({
                'code': 200,
                'msg': message,
                'data': dept
            })
        else:
            return jsonify({
                'code': 400,
                'msg': message,
                'data': None
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'更新失败: {str(e)}',
            'data': None
        })


@dept_bp.route('/delete/<int:dept_id>', methods=['DELETE'])
def delete_dept(dept_id: int):
    """删除部门"""
    try:
        success, message = SysDeptsService.delete_dept(dept_id)

        if success:
            return jsonify({
                'code': 200,
                'msg': message
            })
        else:
            return jsonify({
                'code': 400,
                'msg': message
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'删除失败: {str(e)}'
        })