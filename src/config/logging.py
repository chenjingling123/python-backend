import logging.config
import os

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'ddet.log')

DEFAULT_LOG_LEVEL = 'INFO'

def get_logging_config(log_level: str = DEFAULT_LOG_LEVEL):
    """返回项目的 logging 配置字典。"""
    
    return {
        'version': 1,
        'disable_existing_loggers': False, # 不禁用已有的日志器
        
        'formatters': {
            'standard': {
                # [时间] [级别] [进程/线程] [模块.函数:行号] 消息
                'format': '%(asctime)s [%(levelname)s] [%(process)d/%(threadName)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s'
            },
            'simple': {
                'format': '%(levelname)s: %(message)s'
            },
        },
        
        'handlers': {
            'console': {
                'level': 'DEBUG',  # 控制台输出所有级别的日志
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': LOG_FILE_PATH,
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 5,
                'encoding': 'utf-8',
            },
        },
        
        'loggers': {
            '': { 
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': True,
            },
            'sqlalchemy.engine': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
    }

def configure_logging(log_level: str):
    """初始化 logging 配置。"""
    config = get_logging_config(log_level)
    logging.config.dictConfig(config)
