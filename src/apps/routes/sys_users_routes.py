from logging import getLogger
from flask import request, jsonify, session
from io import BytesIO
import base64
import uuid
import random
import string
import time
from captcha.image import ImageCaptcha
from apps import DDetBlueprint
from db.services.sys_users_service import SysUsersService

logger = getLogger(__name__)

user_bp = DDetBlueprint('sys_users', __name__, url_prefix='/system/user')


# 生成随机验证码
def generate_code(length=4):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@user_bp.route('/getCaptcha', methods=['GET'])
def getCaptcha():
    try:
        # 1 生成验证码
        code = generate_code()

        # 2 生成验证码图片
        image = ImageCaptcha(width=110, height=60)
        data = image.generate(code)

        # 3 转换为 Base64
        buffer = BytesIO()
        buffer.write(data.read())
        img_bytes = buffer.getvalue()

        base64_img = base64.b64encode(img_bytes).decode('utf-8')
        base64_captcha = "data:image/gif;base64," + base64_img

        # 4 生成 captchaId（使用固定的ID或生成新的）
        captcha_id = 'captchaId'  # 保持固定ID，因为使用session不需要多个

        # 5 存入 Session（5分钟过期）
        session['captcha_code'] = code
        session['captcha_expire'] = time.time() + 300  # 记录过期时间

        # 可选：记录日志
        logger.info(f"验证码已生成: {code}")

        return jsonify({
            "base64Captcha": base64_captcha,
            "captchaId": captcha_id
        })

    except Exception as e:
        logger.error(f"getCaptcha error: {e}")
        return jsonify({
            "msg": "captcha generate failed"
        }), 500


@user_bp.route('/login', methods=['POST'])
def login():
    try:
        # 获取请求数据
        data = request.get_json()
        user_input = data.get('captcha')

        # 参数校验
        if not user_input:
            return jsonify({
                "code": 400,
                "msg": "请输入验证码！"
            }), 400

        # 从 Session 获取存储的验证码
        stored_code = session.get('captcha_code')
        expire_time = session.get('captcha_expire', 0)

        # 调试日志
        logger.debug(f"用户输入: {user_input}")
        logger.debug(f"存储的值: {stored_code}")
        logger.debug(f"过期时间: {expire_time}")

        # 检查验证码是否存在
        if stored_code is None:
            return jsonify({
                "code": 400,
                "msg": "验证码不存在，请重新获取"
            })

        # 检查是否过期
        if time.time() > expire_time:
            # 清除过期验证码
            session.pop('captcha_code', None)
            session.pop('captcha_expire', None)
            return jsonify({
                "code": 400,
                "msg": "验证码已过期，请重新获取"
            })

        # 验证验证码（不区分大小写）
        if stored_code.lower() == user_input.lower():
            # 验证成功后删除验证码（一次性使用）
            session.pop('captcha_code', None)
            session.pop('captcha_expire', None)

            # 这里可以继续处理登录逻辑
            # 例如：验证用户名密码等
            # 调用 checkLoginUser 验证用户名密码
            res = {}
            success, result = SysUsersService.checkLoginUser(data, res)

            #return jsonify({
            #    "code": 200,
            #    "msg": "登录成功"
            #})

            if success:
                # 登录成功，可以在这里设置登录状态到 session
                session['user_id'] = result['data']['user']['userId']
                session['username'] = result['data']['user']['username']
                session.permanent = True

                return jsonify(result)
            else:
                return jsonify(result), result.get('code', 400)
        else:
            # 验证失败，可以选择是否删除
            # 为了安全，建议保留让用户可以重试，但限制重试次数
            return jsonify({
                "code": 400,
                "msg": "验证码错误"
            })

    except Exception as e:
        logger.error(f"login error: {e}")
        return jsonify({
            "code": 500,
            "msg": "登录失败"
        }), 500


# 可选：添加一个获取当前验证码状态的路由（用于调试）
@user_bp.route('/captchaStatus', methods=['GET'])
def captchaStatus():
    """检查验证码状态（仅用于调试）"""
    stored_code = session.get('captcha_code')
    expire_time = session.get('captcha_expire', 0)

    if stored_code:
        remaining = max(0, int(expire_time - time.time()))
        return jsonify({
            "exists": True,
            "code": stored_code,  # 调试用，生产环境不应返回
            "expire_in": remaining,
            "is_expired": remaining <= 0
        })
    else:
        return jsonify({
            "exists": False
        })

# ✅ 分页查询
@user_bp.route('/list', methods=['GET'])
def get_user_list():
    """
    获取用户列表（对应 C# 的 list 方法）
    请求参数：
        pageNum: 当前页码
        pageSize: 每页记录数
        username: 用户名（模糊查询）
        phone: 手机号（模糊查询）
        status: 状态
        deptId: 部门ID
    """
    try:
        # 获取请求参数
        page_num = request.args.get('pageNum', 1, type=int)
        page_size = request.args.get('pageSize', 10, type=int)
        username = request.args.get('username', '')
        phone = request.args.get('phone', '')
        status = request.args.get('status', '')
        dept_id = request.args.get('deptId', type=int)

        # 调用 service 获取数据
        result = SysUsersService.get_table_data(
            page_num=page_num,
            page_size=page_size,
            username=username,
            phone=phone,
            status=status,
            dept_id=dept_id
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': {
                'data': [],
                'total': 0,
                'pageNum': page_num if 'page_num' in locals() else 1,
                'pageSize': page_size if 'page_size' in locals() else 10
            }
        })


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """根据ID获取用户详情"""
    try:
        user = SysUsersService.get_user_by_id(user_id)
        if user:
            return jsonify({
                'code': 200,
                'msg': 'success',
                'data': user
            })
        else:
            return jsonify({
                'code': 404,
                'msg': f'用户(ID={user_id})不存在',
                'data': None
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'查询失败: {str(e)}',
            'data': None
        })


@user_bp.route('/add', methods=['POST'])
def add_user():
    """新增用户"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空'
            })

        success, message, user = SysUsersService.add_user(data)

        if success:
            return jsonify({
                'code': 200,
                'msg': message,
                'data': user
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


@user_bp.route('/edit', methods=['PUT'])
def edit_user():
    """编辑用户"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'msg': '请求数据不能为空'
            })

        user_id = data.get('userId')
        if not user_id:
            return jsonify({
                'code': 400,
                'msg': '用户ID不能为空'
            })

        success, message, user = SysUsersService.update_user(user_id, data)

        if success:
            return jsonify({
                'code': 200,
                'msg': message,
                'data': user
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


@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    """删除用户"""
    try:
        success, message = SysUsersService.delete_user(user_id)

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


@user_bp.route('/batchDelete', methods=['DELETE'])
def batch_delete_users():
    """批量删除用户"""
    try:
        data = request.get_json()
        user_ids = data.get('userIds', [])

        if not user_ids:
            return jsonify({
                'code': 400,
                'msg': '请选择要删除的用户'
            })

        success_count = 0
        fail_count = 0

        for user_id in user_ids:
            success, _ = SysUsersService.delete_user(user_id)
            if success:
                success_count += 1
            else:
                fail_count += 1

        return jsonify({
            'code': 200,
            'msg': f'成功删除{success_count}个用户，失败{fail_count}个',
            'data': {
                'success': success_count,
                'fail': fail_count
            }
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'msg': f'批量删除失败: {str(e)}'
        })