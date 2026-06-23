from waitress import serve
from apps import get_app
from config import config, configure_logging

configure_logging(config.log.level)

def entry_point():
    serve(get_app(), host=config.app.host, port=config.app.port)

def development_entry_point():
    get_app().run(host=config.app.host, port=config.app.port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 如果直接运行文件，则默认使用开发模式
    # 如果是生产环境，请使用以下命令运行：
    # >>> ddet-prod
    from logging import getLogger
    logger = getLogger(__name__)
    logger.warning("直接运行 main.py 仅适用于开发环境！生产环境请使用 ddet-prod 命令。")
    development_entry_point()