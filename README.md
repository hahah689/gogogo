# 跨境电商智能客服处理台

这是一个基于 **FastAPI + LangGraph + LangChain + RAG + Qdrant** 的跨境电商智能客服处理项目。

项目主要用于帮助跨境电商卖家处理：

- 商品申诉
- 平台误判分析
- 儿童产品证书误判
- 商品页面合规检查
- 平台沟通邮件生成
- 售后回复
- 知识库问答

---

## 一、项目目录说明


├─ console_web
│  └─ app
│     ├─ main.py                  # FastAPI 启动入口
│     ├─ rag_api.py               # RAG 上传和检索接口
│     └─ templates
│        └─ chat.html             # 前端页面
│
├─ ecommerce_support_agent
│  └─ app
│     ├─ graph.py                 # LangGraph 智能体流程
│     └─ services
│        └─ assistants
│           └─ primary_assistant.py
│
├─ knowledge_engine
│  └─ app
│     └─ vectordb
│        └─ vectordb.py           # Qdrant 连接逻辑
│
├─ compliance_knowledge           # 合规知识库 / FAQ 扩展
├─ case_data                      # 案例数据 / 上传资料 / 本地数据
├─ docker-compose.yml             # Docker 服务配置
├─ pyproject.toml                 # Poetry 依赖配置
└─ README.md
```

---

## 二、运行前准备

请确认电脑已经安装：

- Python
- Poetry
- Docker Desktop
- Git
- VS Code 或其他编辑器

建议使用 Windows PowerShell 运行下面的命令。

---

## 三、进入项目目录

先进入项目根目录。

示例：

```powershell
cd 文件地址
```

---

## 四、安装项目依赖

第一次运行项目，需要先安装依赖：

```powershell
poetry install
```

如果使用文件上传功能，还需要安装：

```powershell
poetry add python-multipart
```

或者：

```powershell
poetry run pip install python-multipart
```

---

## 五、启动 Docker Desktop

先打开 Docker Desktop，等它完全启动。

然后在 PowerShell 里检查 Docker 是否正常：

```powershell
docker ps
```

如果 Docker 报错，可以先执行：

```powershell
wsl --shutdown
```

然后重新打开 Docker Desktop。

---

## 六、启动 Qdrant 向量数据库

本项目使用 Qdrant 作为知识库向量数据库。

在项目根目录执行：

```powershell
docker compose -p ecommerce_support up qdrant -d
```

检查 Qdrant 是否启动成功：

```powershell
docker ps
```

正常情况下应该能看到类似：

```text
ecommerce_support-qdrant-1
0.0.0.0:6333->6333/tcp
```

也可以用下面命令测试：

```powershell
Invoke-RestMethod http://127.0.0.1:6333/collections
```

如果正常，会返回类似：

```text
status ok
```

---

## 七、设置本地代理环境变量

如果你电脑开过代理，项目连接 Qdrant 时可能会出现 `502 Bad Gateway`。

启动 Web 项目前，建议先在 PowerShell 执行：

```powershell
$env:NO_PROXY="localhost,127.0.0.1"
$env:no_proxy="localhost,127.0.0.1"
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
$env:http_proxy=""
$env:https_proxy=""
$env:ALL_PROXY=""
$env:all_proxy=""
$env:QDRANT_URL="http://127.0.0.1:6333"
```

---

## 八、启动 Web 项目

在项目根目录执行：

```powershell
poetry run python -m uvicorn console_web.app.main:app --host 127.0.0.1 --port 8000
```

启动成功后，浏览器打开：

```text
http://127.0.0.1:8000
```

---

## 九、完整启动流程汇总

如果你已经安装过依赖，日常启动只需要按下面顺序执行。

### 第 1 步：进入项目目录

```powershell
cd F:\github\原版客服\原版客服
```

### 第 2 步：启动 Qdrant

```powershell
docker compose -p ecommerce_support up qdrant -d
```

### 第 3 步：设置代理环境变量

```powershell
$env:NO_PROXY="localhost,127.0.0.1"
$env:no_proxy="localhost,127.0.0.1"
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
$env:http_proxy=""
$env:https_proxy=""
$env:ALL_PROXY=""
$env:all_proxy=""
$env:QDRANT_URL="http://127.0.0.1:6333"
```

### 第 4 步：启动后端 Web 服务

```powershell
poetry run python -m uvicorn console_web.app.main:app --host 127.0.0.1 --port 8000
```

### 第 5 步：打开浏览器

```text
http://127.0.0.1:8000
```

---

## 十、关闭项目

### 1. 关闭 Web 服务

在运行 Web 服务的 PowerShell 窗口中按：

```text
Ctrl + C
```

### 2. 关闭 Qdrant

在项目根目录执行：

```powershell
docker compose -p ecommerce_support down
`



这个项目是一个面向跨境电商卖家的智能客服处理系统，主要用于商品申诉、平台误判分析、商品页面合规检查、客服邮件生成和售后回复等场景。技术上，项目基于 FastAPI 构建后端服务，使用 LangGraph 搭建多智能体工作流，将不同业务场景拆分为主助手、申诉处理、页面检查、资料整理等智能体模块；同时接入大语言模型完成问题理解、处理建议生成和中英文申诉邮件撰写。项目还引入 RAG 检索增强生成机制，使用 Qdrant 向量数据库存储平台规则、申诉模板和商品资料，用户提问时系统会先从知识库检索相关内容，再结合大模型生成更准确的业务回复。前端采用企业级处理台布局，包含业务场景中心、智能对话区、材料填写区和知识库上传区，使系统从普通聊天机器人升级为可用于实际跨境电商运营的智能客服工作台。
