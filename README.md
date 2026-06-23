# 科研项目管理系统后端

这是一个面向科研项目管理场景的 Python 后端项目，基于 Flask、SQLAlchemy 和 MySQL 构建，提供项目档案、组织部门、用户权限、菜单配置、岗位信息、设备信息等基础管理能力，可作为科研管理平台、实验室项目台账系统或教学科研数据管理系统的后端服务。

## 功能概览

- 科研项目信息管理：支持项目列表查询、新增、更新和删除。
- 用户与登录管理：提供验证码、登录认证、用户列表和用户维护接口。
- 组织部门管理：支持部门树、部门列表、角色部门树选择等接口。
- 菜单与权限管理：支持系统菜单、前端路由菜单、角色菜单树等数据接口。
- 岗位与字典数据管理：提供基础系统配置数据维护能力。
- 设备信息管理：支持设备类数据的列表、新增、更新和删除。
- 统一响应结构：通过 Pydantic 模型封装接口返回数据。
- 数据库访问层：使用 SQLAlchemy 组织模型和服务层逻辑。

## 技术栈

- Python 3.9
- Flask
- SQLAlchemy
- PyMySQL
- Pydantic
- Pydantic Settings
- Waitress
- MySQL

## 项目结构

```text
.
├── .env.default              # 默认环境变量示例
├── pyproject.toml            # 项目依赖和启动命令配置
├── README.md                 # 项目说明文档
├── vueworkdb_teach.sql       # 数据库初始化脚本
├── src/
│   ├── main.py               # 应用入口
│   ├── apps/                 # Flask 应用与路由模块
│   │   ├── routes/           # 接口路由
│   │   └── schemas/          # 请求/响应数据模型
│   ├── config/               # 配置与日志初始化
│   ├── db/                   # 数据库模型与服务层
│   │   ├── models/           # SQLAlchemy 模型
│   │   └── services/         # 业务数据操作
│   └── tools/                # 通用工具函数
└── tests/                    # 测试代码
```

## 环境准备

请先安装 Python 3.9。

创建并启用虚拟环境：

```bash
python -m venv venv
venv\Scripts\activate
```

安装项目依赖：

```bash
pip install -e .
```

## 配置说明

项目使用 `.env` 文件读取运行配置。首次运行前可以复制默认配置：

```bash
copy .env.default .env
```

然后根据本地 MySQL 环境修改 `.env` 中的数据库地址、用户名、密码、数据库名、应用端口等配置。

`.env` 文件包含本地敏感配置，已被 `.gitignore` 忽略，不应提交到仓库。

## 数据库初始化

项目根目录提供了数据库脚本：

```text
vueworkdb_teach.sql
```

可以使用 MySQL 客户端或数据库管理工具导入该脚本，创建系统所需的数据表和初始数据。

## 启动服务

开发模式启动：

```bash
ddet-dev
```

也可以直接运行入口文件：

```bash
python src/main.py
```

生产模式建议使用：

```bash
ddet-prod
```

服务监听地址和端口由 `.env` 中的应用配置决定。

## 主要接口模块

| 模块 | 路由前缀 | 说明 |
| --- | --- | --- |
| 用户管理 | `/system/user` | 登录、验证码、用户列表、用户维护 |
| 部门管理 | `/system/dept` | 部门树、部门列表、部门新增修改删除 |
| 菜单管理 | `/system/menu` | 菜单列表、菜单树、角色菜单树 |
| 岗位管理 | `/system/post` | 岗位列表、新增、更新、删除 |
| 科研项目 | `/ProjectInfo` | 科研项目信息列表、新增、更新、删除 |
| 设备管理 | `/device/falldowndevice` | 设备数据列表、新增、更新、删除 |

## 开发说明

- 路由代码位于 `src/apps/routes/`。
- 接口数据模型位于 `src/apps/schemas/`。
- 数据库表模型位于 `src/db/models/`。
- 数据库业务操作位于 `src/db/services/`。
- 应用入口位于 `src/main.py`。

新增科研业务模块时，建议按以下顺序组织代码：

1. 在 `src/db/models/` 中定义数据库模型。
2. 在 `src/db/services/` 中实现查询、新增、更新、删除等业务方法。
3. 在 `src/apps/schemas/` 中定义请求和响应模型。
4. 在 `src/apps/routes/` 中注册 Flask 路由。
5. 在 `src/apps/__init__.py` 中引入路由模块，确保蓝图注册生效。

## 版本控制说明

仓库不会提交以下本地文件：

- `.env`
- Python 缓存文件
- 日志文件
- 构建产物
- IDE 本地配置

提交前可以检查状态：

```bash
git status
```
