"""
应用配置管理模块

如果需要修改配置，请参考项目根目录下的 .env.default 文件
创建一个 .env 文件并覆盖对应的配置项

"""
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_DEFAULT_FILE = PROJECT_ROOT / '.env.default'
ENV_FILE = PROJECT_ROOT / '.env'


class _AppConfig(BaseModel):
    host: str = '0.0.0.0'
    port: int = 5000

class _LogConfig(BaseModel):
    level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL


class _MySQLConfig(BaseModel):
    username: str = 'teachuser'
    password: str = 'Teachuser!@#123'
    host: str = 'db.wulianxx.com'
    port: int = 3306
    database: str = 'vueworkdb_teach'

    @property
    def password_quoted(self) -> str:
        return quote_plus(self.password)

# 如果需要添加新的配置项，可以在这里继续添加新的配置类
# 然后在 _Config 类中添加相应的字段

class _SqliteConfig(BaseModel):

    enable: bool = False
    """是否启用 SQLite 数据库，启用后会忽略 MySQL 配置"""

    file_path: str = 'data/sqlite.db'



# 整体配置类
class _Config(BaseSettings):
    """
    应用程序配置类，包含所有子配置。
    会从 .env.default 以及 .env 文件中加载配置，后者会覆盖前者。
    支持嵌套的环境变量，例如 APP_HOST, MYSQL_USERNAME 等。

    如果需要添加新的配置项，可以在这里继续添加新的字段。
    """
    model_config = SettingsConfigDict(
        env_file=[str(ENV_DEFAULT_FILE), str(ENV_FILE)],
        env_file_encoding='utf-8',
        env_nested_delimiter='_',
    )

    base_path: Path = Field(default_factory=lambda: PROJECT_ROOT)
    """应用程序的基础路径"""

    # 以 app 命名后，应用就会从 APP_ 为前缀的环境变量中加载配置
    # mysql 则对应 MYSQL_ 前缀
    # 注意：嵌套的配置类中的字段名**不能**使用下划线，否则无法正确加载
    log: _LogConfig = Field(default_factory=_LogConfig)
    app: _AppConfig = Field(default_factory=_AppConfig)
    mysql: _MySQLConfig = Field(default_factory=_MySQLConfig)
    sqlite: _SqliteConfig = Field(default_factory=_SqliteConfig)

config = _Config()
