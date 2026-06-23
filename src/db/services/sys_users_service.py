import hashlib
from datetime import datetime, timedelta  # 同时导入 datetime 和 timedelta
from typing import Optional, Tuple, Any, List, Dict

import jwt
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import engine
from db.models.sys_users import SysUsers  # 导入 SysUsers 模型


class SysUsersService:
    """系统用户服务类"""

    # ✅ 查询所有用户（不分页、不过滤）
    @staticmethod
    def list_all_users() -> List[SysUsers]:
        """查询所有用户记录"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(SysUsers.delete_time.is_(None)).all()

    # ✅ 分页查询用户
    @staticmethod
    def list_users(
            filters: Optional[dict] = None,
            page_num: int = 1,
            page_size: int = 10
    ) -> Tuple[int, List[SysUsers]]:
        """分页查询用户记录"""
        with Session(engine) as session:
            # 基础查询：排除已删除的用户
            base_query = session.query(SysUsers).filter(SysUsers.delete_time.is_(None))
            sql_filters = []

            if filters:
                for key, value in filters.items():
                    # 如果字段不存在或值为空，跳过
                    if value is None or not hasattr(SysUsers, key):
                        continue

                    # 特殊字段处理
                    if key == 'username' or key == 'nick_name' or key == 'phone' or key == 'email':
                        # 字符串字段使用模糊查询
                        sql_filters.append(getattr(SysUsers, key).like(f"%{value}%"))
                    elif key == 'status':
                        # 状态精确查询
                        sql_filters.append(getattr(SysUsers, key) == value)
                    elif key == 'dept_id' or key == 'role_id':
                        # 部门ID和角色ID精确查询
                        sql_filters.append(getattr(SysUsers, key) == value)
                    elif key == 'role_ids':
                        # 多角色ID模糊查询（包含某个角色）
                        sql_filters.append(getattr(SysUsers, key).like(f"%{value}%"))
                    elif key == 'date_range' and isinstance(value, list) and len(value) == 2:
                        # 日期范围查询
                        start_date, end_date = value
                        if start_date:
                            sql_filters.append(SysUsers.create_time >= start_date)
                        if end_date:
                            sql_filters.append(SysUsers.create_time <= end_date)
                    else:
                        # 其他字段精确查询
                        sql_filters.append(getattr(SysUsers, key) == value)

            if sql_filters:
                base_query = base_query.filter(and_(*sql_filters))

            total = base_query.count()

            records = (
                base_query
                .order_by(SysUsers.user_id.desc())  # 按ID倒序，最新的在前面
                .offset((page_num - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return total, records

    # ✅ 新增用户
    @staticmethod
    def add_user(user: SysUsers) -> Tuple[bool, str, Optional[SysUsers]]:
        """新增用户"""
        with Session(engine) as session:
            try:
                # 检查用户名是否已存在
                existing = session.query(SysUsers).filter(
                    SysUsers.username == user.username,
                    SysUsers.delete_time.is_(None)
                ).first()
                if existing:
                    return False, "用户名已存在", None

                # 检查手机号是否已存在
                if user.phone:
                    existing_phone = session.query(SysUsers).filter(
                        SysUsers.phone == user.phone,
                        SysUsers.delete_time.is_(None)
                    ).first()
                    if existing_phone:
                        return False, "手机号已存在", None

                # 检查邮箱是否已存在
                if user.email:
                    existing_email = session.query(SysUsers).filter(
                        SysUsers.email == user.email,
                        SysUsers.delete_time.is_(None)
                    ).first()
                    if existing_email:
                        return False, "邮箱已存在", None

                # 设置创建时间
                user.create_time = datetime.now()
                user.status = user.status or '0'  # 默认正常状态

                session.add(user)
                session.commit()
                session.refresh(user)
                return True, "添加成功", user

            except IntegrityError as e:
                session.rollback()
                return False, f"数据库错误: {str(e)}", None
            except Exception as e:
                session.rollback()
                return False, f"添加失败: {str(e)}", None

    # ✅ 根据ID查询单个用户
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[SysUsers]:
        """根据ID查询单个用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(
                SysUsers.user_id == user_id,
                SysUsers.delete_time.is_(None)
            ).first()

    # ✅ 根据用户名查询用户
    @staticmethod
    def get_user_by_username(username: str) -> Optional[SysUsers]:
        """根据用户名查询用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(
                SysUsers.username == username,
                SysUsers.delete_time.is_(None)
            ).first()

    # ✅ 根据手机号查询用户
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[SysUsers]:
        """根据手机号查询用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(
                SysUsers.phone == phone,
                SysUsers.delete_time.is_(None)
            ).first()

    # ✅ 查询所有用户（返回列表）
    @staticmethod
    def get_all_users() -> List[SysUsers]:
        """查询所有未删除的用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(SysUsers.delete_time.is_(None)).all()

    # ✅ 更新用户
    @staticmethod
    def update_user(user: SysUsers) -> Tuple[bool, str, Optional[SysUsers]]:
        """更新用户信息"""
        with Session(engine) as session:
            try:
                existing = session.query(SysUsers).filter(
                    SysUsers.user_id == user.user_id,
                    SysUsers.delete_time.is_(None)
                ).first()

                if not existing:
                    return False, f"用户(ID={user.user_id})不存在", None

                # 检查用户名唯一性（如果修改了用户名）
                if user.username and user.username != existing.username:
                    username_exists = session.query(SysUsers).filter(
                        SysUsers.username == user.username,
                        SysUsers.user_id != user.user_id,
                        SysUsers.delete_time.is_(None)
                    ).first()
                    if username_exists:
                        return False, "用户名已存在", None

                # 检查手机号唯一性（如果修改了手机号）
                if user.phone and user.phone != existing.phone:
                    phone_exists = session.query(SysUsers).filter(
                        SysUsers.phone == user.phone,
                        SysUsers.user_id != user.user_id,
                        SysUsers.delete_time.is_(None)
                    ).first()
                    if phone_exists:
                        return False, "手机号已存在", None

                # 检查邮箱唯一性（如果修改了邮箱）
                if user.email and user.email != existing.email:
                    email_exists = session.query(SysUsers).filter(
                        SysUsers.email == user.email,
                        SysUsers.user_id != user.user_id,
                        SysUsers.delete_time.is_(None)
                    ).first()
                    if email_exists:
                        return False, "邮箱已存在", None

                # 更新字段（排除空值和特定字段）
                exclude_fields = ['user_id', 'create_time', 'delete_time']
                for key, value in user.__dict__.items():
                    if key.startswith("_") or key in exclude_fields:
                        continue
                    if value is not None:  # 只更新非空字段
                        setattr(existing, key, value)

                # 更新修改时间
                existing.update_time = datetime.now()

                session.commit()
                session.refresh(existing)
                return True, "更新成功", existing

            except IntegrityError as e:
                session.rollback()
                return False, f"数据库错误: {str(e)}", None
            except Exception as e:
                session.rollback()
                return False, f"更新失败: {str(e)}", None

    # ✅ 软删除用户
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """软删除用户（设置delete_time）"""
        with Session(engine) as session:
            try:
                user = session.query(SysUsers).filter(
                    SysUsers.user_id == user_id,
                    SysUsers.delete_time.is_(None)
                ).first()

                if not user:
                    return False, f"用户(ID={user_id})不存在或已删除"

                # 软删除：设置删除时间
                user.delete_time = datetime.now()
                session.commit()
                return True, "删除成功"

            except Exception as e:
                session.rollback()
                return False, f"删除失败: {str(e)}"

    # ✅ 硬删除用户（永久删除）
    @staticmethod
    def hard_delete_user(user_id: int) -> Tuple[bool, str]:
        """硬删除用户（从数据库中永久删除）"""
        with Session(engine) as session:
            try:
                user = session.query(SysUsers).filter(SysUsers.user_id == user_id).first()
                if not user:
                    return False, f"用户(ID={user_id})不存在"

                session.delete(user)
                session.commit()
                return True, "永久删除成功"

            except Exception as e:
                session.rollback()
                return False, f"删除失败: {str(e)}"

    # ✅ 批量删除用户
    @staticmethod
    def batch_delete_users(user_ids: List[int]) -> Tuple[int, str]:
        """批量软删除用户"""
        with Session(engine) as session:
            try:
                users = session.query(SysUsers).filter(
                    SysUsers.user_id.in_(user_ids),
                    SysUsers.delete_time.is_(None)
                ).all()

                if not users:
                    return 0, "未找到可删除的用户"

                now = datetime.now()
                for user in users:
                    user.delete_time = now

                session.commit()
                return len(users), f"成功删除{len(users)}个用户"

            except Exception as e:
                session.rollback()
                return 0, f"批量删除失败: {str(e)}"

    # ✅ 更新用户状态
    @staticmethod
    def update_user_status(user_id: int, status: str) -> Tuple[bool, str]:
        """更新用户状态"""
        with Session(engine) as session:
            try:
                user = session.query(SysUsers).filter(
                    SysUsers.user_id == user_id,
                    SysUsers.delete_time.is_(None)
                ).first()

                if not user:
                    return False, f"用户(ID={user_id})不存在"

                user.status = status
                user.update_time = datetime.now()
                session.commit()
                return True, "状态更新成功"

            except Exception as e:
                session.rollback()
                return False, f"状态更新失败: {str(e)}"

    # ✅ 获取用户ID到用户名的映射
    @staticmethod
    def get_user_mapping() -> Dict[int, str]:
        """获取用户ID到用户名的映射"""
        with Session(engine) as session:
            users = session.query(SysUsers).filter(SysUsers.delete_time.is_(None)).all()
            return {user.user_id: user.username for user in users}

    # ✅ 获取用户ID到昵称的映射
    @staticmethod
    def get_user_nickname_mapping() -> Dict[int, str]:
        """获取用户ID到昵称的映射"""
        with Session(engine) as session:
            users = session.query(SysUsers).filter(SysUsers.delete_time.is_(None)).all()
            return {user.user_id: user.nick_name or user.username for user in users}

    # ✅ 根据部门ID查询用户
    @staticmethod
    def get_users_by_dept(dept_id: int) -> List[SysUsers]:
        """根据部门ID查询用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(
                SysUsers.dept_id == dept_id,
                SysUsers.delete_time.is_(None)
            ).all()

    # ✅ 根据角色ID查询用户
    @staticmethod
    def get_users_by_role(role_id: int) -> List[SysUsers]:
        """根据角色ID查询用户"""
        with Session(engine) as session:
            return session.query(SysUsers).filter(
                or_(
                    SysUsers.role_id == role_id,
                    SysUsers.role_ids.like(f"%{role_id}%")
                ),
                SysUsers.delete_time.is_(None)
            ).all()


#下面是登录相关函数：
    # JWT配置
    JWT_SECRET = "your-secret-key-here"  # 建议从配置文件读取
    JWT_ALGORITHM = "HS256"

    @staticmethod
    def checkLoginUser(req: Dict[str, Any], res: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        检查用户登录

        Args:
            req: 登录请求数据，包含 username, password
            res: 响应数据对象

        Returns:
            (是否成功, 响应数据)
        """
        if res is None:
            res = {}

        # 初始化响应数据结构
        res['data'] = {
            'user': None,
            'permissions': [],
            'menus': [],
            'expire': 0,
            'token': ''
        }

        try:
            with Session(engine) as session:
                # 1. 查询用户（不区分大小写，忽略空格）
                username = req.get('username', '').strip()
                if not username:
                    res['code'] = 400
                    res['msg'] = "用户名不能为空"
                    return False, res

                # 查询用户（精确匹配，不区分大小写）
                user = session.query(SysUsers).filter(
                    SysUsers.username.ilike(username),  # 精确匹配不区分大小写
                    SysUsers.delete_time.is_(None)
                ).first()

                if not user:
                    res['code'] = 400
                    res['msg'] = "用户不存在"
                    return False, res

                # 2. 检查密码是否为空
                if not user.password:
                    res['code'] = 400
                    res['msg'] = "用户密码为空"
                    return False, res

                # 3. 密码验证
                input_pwd = req.get('password', '').strip()
                if not input_pwd:
                    res['code'] = 400
                    res['msg'] = "密码不能为空"
                    return False, res

                # 判断是否需要加密（如果长度小于32，表示可能是明文，需要加密）
                if len(input_pwd) < 32:
                    # 进行 MD5 加密
                    md5 = hashlib.md5()
                    md5.update(input_pwd.encode('utf-8'))
                    input_pwd = md5.hexdigest().upper()

                # 比较密码（不区分大小写）
                if user.password.upper() != input_pwd.upper():
                    res['code'] = 400
                    res['msg'] = "密码不正确"
                    return False, res

                # 4. 检查用户角色
                if not user.role_ids:
                    res['code'] = 400
                    res['msg'] = "用户角色为空"
                    return False, res

                # 5. 获取用户信息（转换为指定格式）
                res['data']['user'] = {
                    'userId': user.user_id,
                    'nickName': user.nick_name or user.username,
                    'phone': user.phone,
                    'roleId': user.role_id,
                    'salt': user.salt,
                    'avatar': user.avatar,
                    'sex': user.sex,
                    'email': user.email,
                    'deptId': user.dept_id,
                    'postId': user.post_id,
                    'createBy': user.create_by,
                    'updateBy': user.update_by,
                    'remark': user.remark,
                    'status': user.status,
                    'create_time': user.create_time.strftime('%Y-%m-%dT%H:%M:%S') if user.create_time else None,
                    'update_time': user.update_time.strftime('%Y-%m-%dT%H:%M:%S') if user.update_time else None,
                    'delete_time': user.delete_time.strftime('%Y-%m-%dT%H:%M:%S') if user.delete_time else None,
                    'username': user.username,
                    'password': user.password,
                    'roleIds': user.role_ids,
                    'postIds': user.post_ids
                }

                # 6. 解析角色ID列表
                role_ids_str = user.role_ids  # 保存原始的字符串形式
                role_ids = [int(rid.strip()) for rid in role_ids_str.split(',') if rid.strip()]

                # 7. 获取菜单和权限
                try:
                    # 调用 SysMenusService.get_sys_menus_by_role_ids 获取菜单列表
                    from .sys_menus_service import SysMenusService  # 确保导入正确
                    menus_list = SysMenusService.get_sys_menus_by_role_ids(role_ids_str)

                    # 保存menu_type值为非‘F'的菜单，F的起始不是菜单
                    no_F_menus_list = []
                    # 收集权限
                    permissions = []
                    for menu in menus_list:
                        if menu.permission and menu.permission.strip():
                            permissions.append(menu.permission.strip())

                        if menu.menu_type and menu.menu_type.upper() != 'F':
                            no_F_menus_list.append(menu)

                    # 构建菜单树
                    from .sys_menus_service import SysMenusService
                    menu_tree = SysMenusService.get_menus_tree(no_F_menus_list)

                    res['data']['menus'] = menu_tree
                    res['data']['permissions'] = permissions

                except Exception as e:
                    res['code'] = 500
                    res['msg'] = f"获取菜单权限失败: {str(e)}"
                    return False, res

                # 8. 计算过期时间（7天后，从1970-01-01 08:00:00开始计算）
                start_date = datetime(1970, 1, 1, 8, 0, 0)
                end_date = datetime.now() + timedelta(days=7)
                seconds = (end_date - start_date).total_seconds()
                res['data']['expire'] = int(seconds)

                # 9. 生成JWT token
                token_payload = {
                    'unique_name': user.username,
                    'nbf': int(datetime.now().timestamp()),
                    'exp': int((datetime.now() + timedelta(minutes=30)).timestamp()),  # token 30分钟过期
                    'iat': int(datetime.now().timestamp())
                }
                token = jwt.encode(
                    token_payload,
                    SysUsersService.JWT_SECRET,
                    algorithm=SysUsersService.JWT_ALGORITHM
                )
                res['data']['token'] = token

                res['code'] = 200
                res['msg'] = "success"
                return True, res

        except Exception as e:
            res['code'] = 500
            res['msg'] = f"登录验证失败: {str(e)}"
            return False, res


    @staticmethod
    def get_table_data(
            page_num: Optional[int] = 1,
            page_size: Optional[int] = 10,
            username: Optional[str] = None,
            phone: Optional[str] = None,
            status: Optional[str] = None,
            dept_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        获取用户表格数据（对应 C# 的 GetTableData 方法）

        Args:
            page_num: 当前页码
            page_size: 每页记录数
            username: 用户名（模糊查询）
            phone: 手机号（模糊查询）
            status: 状态
            dept_id: 部门ID

        Returns:
            响应数据字典
        """
        try:
            with Session(engine) as session:
                # 构建查询条件
                query = session.query(SysUsers).filter(SysUsers.delete_time.is_(None))

                # 添加过滤条件（对应 C# 的 PredicateExtensions）
                filters = []

                # 用户名模糊查询
                if username and username != 'null' and username.strip():
                    filters.append(SysUsers.username.like(f'%{username}%'))

                # 手机号模糊查询
                if phone and phone != 'null' and phone.strip():
                    filters.append(SysUsers.phone.like(f'%{phone}%'))

                # 部门ID精确查询（排除0和null）
                if dept_id is not None and dept_id > 0:
                    filters.append(SysUsers.dept_id == dept_id)

                # 状态精确查询
                if status and status != 'null' and status.strip():
                    filters.append(SysUsers.status == status)

                # 应用所有过滤条件
                if filters:
                    query = query.filter(and_(*filters))

                # 获取总记录数
                total = query.count()

                # 分页查询（按用户名排序，对应 C# 的 r => r.Username, true）
                records = query.order_by(SysUsers.username).offset(
                    (page_num - 1) * page_size
                ).limit(page_size).all()

                # 转换为字典列表（对应 C# 的 _mapper.Map）
                results = [user.to_dict() for user in records]

                # 构建返回数据（对应 C# 的 VueTable）
                table_data = {
                    'data': results,
                    'total': total,
                    'pageNum': page_num,
                    'pageSize': page_size
                }

                return {
                    'code': 200,
                    'msg': 'success',
                    'data': table_data
                }

        except Exception as e:
            return {
                'code': 500,
                'msg': f'查询失败: {str(e)}',
                'data': {
                    'data': [],
                    'total': 0,
                    'pageNum': page_num,
                    'pageSize': page_size
                }
            }


    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """根据ID获取用户"""
        with Session(engine) as session:
            user = session.query(SysUsers).filter(
                SysUsers.user_id == user_id,
                SysUsers.delete_time.is_(None)
            ).first()
            return user.to_dict() if user else None


    @staticmethod
    def add_user(user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """新增用户"""
        with Session(engine) as session:
            try:
                # 检查用户名是否已存在
                existing = session.query(SysUsers).filter(
                    SysUsers.username == user_data.get('username'),
                    SysUsers.delete_time.is_(None)
                ).first()
                if existing:
                    return False, "用户名已存在", None

                # 创建新用户
                new_user = SysUsers(
                    username=user_data.get('username'),
                    nick_name=user_data.get('nickName'),
                    phone=user_data.get('phone'),
                    email=user_data.get('email'),
                    dept_id=user_data.get('deptId'),
                    role_ids=user_data.get('roleIds'),
                    post_ids=user_data.get('postIds'),
                    status=user_data.get('status', '0'),
                    create_time=datetime.now()
                )

                session.add(new_user)
                session.commit()
                session.refresh(new_user)

                return True, "添加成功", new_user.to_dict()

            except Exception as e:
                session.rollback()
                return False, f"添加失败: {str(e)}", None


    @staticmethod
    def update_user(user_id: int, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """更新用户"""
        with Session(engine) as session:
            try:
                user = session.query(SysUsers).filter(
                    SysUsers.user_id == user_id,
                    SysUsers.delete_time.is_(None)
                ).first()

                if not user:
                    return False, f"用户(ID={user_id})不存在", None

                # 更新字段
                for key, value in user_data.items():
                    if hasattr(user, key) and value is not None:
                        setattr(user, key, value)

                user.update_time = datetime.now()
                session.commit()
                session.refresh(user)

                return True, "更新成功", user.to_dict()

            except Exception as e:
                session.rollback()
                return False, f"更新失败: {str(e)}", None


    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """软删除用户"""
        with Session(engine) as session:
            try:
                user = session.query(SysUsers).filter(
                    SysUsers.user_id == user_id,
                    SysUsers.delete_time.is_(None)
                ).first()

                if not user:
                    return False, f"用户(ID={user_id})不存在"

                user.delete_time = datetime.now()
                session.commit()

                return True, "删除成功"

            except Exception as e:
                session.rollback()
                return False, f"删除失败: {str(e)}"