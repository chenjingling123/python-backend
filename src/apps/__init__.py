"""
本模块用于初始化 flask 应用程序实例。
"""

from flask import Flask, Blueprint
from pydantic_core import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from pymysql.err import Error as PyMysqlException
import werkzeug.serving

werkzeug.serving.BaseWSGIServer.allow_reuse_address = False

_ddet_app = Flask('ddet-app')

_ddet_app.config['SECRET_KEY'] = 'your-secret-key-here'  # 请使用一个复杂的随机字符串

_blueprints: list[Blueprint] = []

def get_app() -> Flask:
    """获取并返回配置好的 Flask 应用实例"""
    for bp in _blueprints:
        _ddet_app.register_blueprint(bp)
    _blueprints.clear()

    @_ddet_app.errorhandler(ValidationError)
    def handle_validation_error(e: ValidationError):
        logger.exception("Validation error")
        return CommonResponse.fail(message=str(*e.errors()))
    
    @_ddet_app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e: SQLAlchemyError):
        logger.exception("Database error")
        return CommonResponse.fail(500, message="数据库操作失败: " + str(*e.args))
    
    @_ddet_app.errorhandler(PyMysqlException)
    def handle_pymysql_error(e: PyMysqlException):
        logger.exception("MySQL error")
        return CommonResponse.fail(500, message="MySQL操作失败: " + str(*e.args))

    # 全局异常处理
    @_ddet_app.errorhandler(Exception)
    def handle_global_exception(e):
        logger.exception("Global error")
        return CommonResponse.fail(500, message=str(e))

    return _ddet_app

class DDetBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _blueprints.append(self)


## 在此处导入所有定义的蓝图 ##
from apps.routes.sys_users_routes import *
from apps.routes.sys_depts_routes import *
from apps.routes.sys_menus_routes import *
from apps.routes.sys_posts_routes import *
from apps.routes.falldown_device_routes import *
from apps.routes.project_info_routes import *
