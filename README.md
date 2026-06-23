# Geo-Redline-Drone-Detection

用于地理生态红线无人机检测的后端项目，实现对无人机航拍数据的处理与分析。

## 📂 项目结构
```
.env.default              # 默认环境变量文件，使用时可以先拷贝到 .env 中再进行配置
.env                      # 环境变量文件，实现管理不同环境的配置
pyproject.toml            # 定义项目依赖、元数据和构建配置
src/
├── apps/                 # 🌐 应用层：Web API 路由和数据传输对象
│   └── schemas/          #     定义 API 请求和响应数据结构
├── config/               # ⚙️ 配置管理：项目设置和配置加载逻辑
├── db/                   # 💾 数据层：数据库模型和操作
│   └── services/         #     数据库服务（如 WarningActService）
├── ml_models/            # 🤖 模型层：机器学习模型逻辑和资源
│   ├── services/         #     模型操作服务（训练、推理）
│   ├── executors/        #     模型训练的实现
│   ├── configs/          #     不同下游模型的配置
│   └── weights/          #     YOLO 模型权重文件或者清单 (.pt, .yaml)
└── tools/                # 🛠️ 通用工具：项目共用的辅助函数或自定义类
tests/                    # 🧪 单元测试等
```

## 🛠️ 环境准备与启动

1. **安装 Python 3.9 版本**

2. **创建虚拟环境（可选，推荐）**

   创建并启用虚拟环境，以 Windows Command Prompt 为例：

   ```bash
   python -m venv venv
   venv\Scripts\activate.bat
   ```

   或者使用 conda 创建虚拟环境：

   ```bash
   conda create --name ddet python=3.9
   conda activate ddet
   ```

3. **安装项目**

   ```bash
   pip install -e .
   ```

   ```bash
   # 如果需要调试模型训练，请使用以下命令安装额外的依赖
   pip install -e .[yolo]
   ```

   > -e 表示以可编辑的模式安装， 不需要修改代码的情况下可以省略

4. **启动应用（调试模式）**

   ```bash
   ddet-dev
   
   # 或者直接运行应用入口文件（调试模式）
   # >>> python src/main.py
   ```

   > 如果是生产模式，请**务必**使用 `ddet-prod` 命令进行启动

## ⚙️ 添加项目依赖

项目使用 **`pyproject.toml`** 文件来定义所有依赖项。在添加新的依赖之前，请遵循以下步骤：

### 1. 添加核心依赖

核心依赖是指项目在所有环境中运行所需的包。

1. **编辑 `pyproject.toml`：** 打开 `pyproject.toml` 文件，找到 `[project.dependencies]` 部分，并添加新的包名及其版本约束（例如 `"new-library>=1.0.0"`）。

   ```toml
   [project]
   dependencies = [
       # ..., 其他已经存在的包
       "new-library>=1.0.0",
   ]
   ```

2. **更新本地环境：** 在项目根目录，重新运行安装命令来更新您的本地虚拟环境：

   ```bash
   pip install -e .
   ```

### 2. 添加可选依赖

可选依赖用于区分特定环境（例如 `cpu` 或 `gpu`）所需的包。

1. **编辑 `pyproject.toml`：** 在相应的组（`[project.optional-dependencies.gpu]`）下添加新的包名和版本约束。

   ```toml
   [project.optional-dependencies]
   cpu = [
   	# 为 cpu 环境下添加的包
   ]
   gpu = [
   	# 为 gpu 环境下添加的包
   ]
   ```

2. **更新本地环境：** 要安装包含这些可选依赖的完整环境，请使用方括号语法：

   ```bash
   # 例如：安装核心依赖和 cpu 依赖
   pip install -e .[cpu]
   ```

### 3. 完成提交

添加依赖后，请确保已将 **`pyproject.toml`** 文件中的所有修改提交到版本控制。
