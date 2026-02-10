# MonkeyUI

[English](README.md)

一个使用 **React 19** 和 **Django 6** 构建的现代全栈应用，集成了 AI/LLM、pgvector 向量搜索以及 Celery 异步任务处理。

---

## 技术栈

| 层级 | 技术 |
|---|---|
| **前端** | React 19 · Vite 6 · TailwindCSS · Shadcn/ui · react-i18next |
| **后端** | Django 6 · Django REST Framework · Celery · drf-spectacular |
| **数据库** | PostgreSQL 16 · pgvector |
| **基础设施** | Docker Compose · Redis · uv · Fly.io |

## 项目结构

```
monkeyui/
├── frontend/           # React + Vite 前端应用
│   ├── src/
│   │   ├── components/ # React 组件（含 Shadcn/ui）
│   │   ├── locales/    # 国际化翻译文件（en/zh）
│   │   └── lib/        # 工具函数
│   └── public/
├── backend/            # Django + DRF 后端 API
│   ├── config/         # Django 项目配置
│   ├── apps/           # Django 应用模块
│   └── locale/         # 后端国际化文件
├── docs/               # 文档
├── docker-compose.yml  # 全栈 Docker 配置
├── Dockerfile          # 多阶段生产构建
├── setup.sh            # 自动化安装脚本
└── setup-auth.sh       # 认证系统安装脚本
```

详细结构请参阅 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)。

## 快速开始

### 前置要求

| 工具 | 版本 | 安装方式 |
|---|---|---|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.14+ | https://www.python.org |
| PostgreSQL | 15+（含 pgvector） | `brew install postgresql pgvector`（macOS） |
| uv | 最新版 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Redis | 7+ | `brew install redis`（macOS）或使用 Docker |

### 方式 A：Docker Compose（推荐）

最快的启动方式——无需在本地安装 PostgreSQL、Redis 或 Python：

```bash
# 启动所有服务（PostgreSQL、Redis、后端、Celery Worker、前端）
docker compose up --build
```

| 服务 | 地址 |
|---|---|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档（Swagger） | http://localhost:8000/api/docs/ |

### 方式 B：自动化本地安装

```bash
# 运行安装脚本（检查前置要求、安装依赖）
./setup.sh
```

然后按照终端输出的"下一步"提示创建数据库、运行迁移并启动服务。

### 方式 C：手动本地安装

#### 1. 数据库

```bash
# macOS
brew install postgresql pgvector
brew services start postgresql

# 创建数据库并启用 pgvector
createdb monkeyui_dev
psql monkeyui_dev -c 'CREATE EXTENSION vector;'
```

#### 2. 后端

```bash
cd backend

# 使用 uv 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的数据库凭据

# 运行迁移并创建管理员用户
uv run python manage.py migrate
uv run python manage.py createsuperuser

# 启动开发服务器
uv run python manage.py runserver
```

后端 API 地址：http://localhost:8000

#### 3. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端地址：http://localhost:5173

#### 4. Celery Worker（可选——用于异步任务）

```bash
# 确保 Redis 已经运行
cd backend
uv run celery -A config worker --loglevel=info
```

## 开发

### 同时运行前后端

```bash
# 终端 1 — 前端
cd frontend && npm run dev

# 终端 2 — 后端
cd backend && uv run python manage.py runserver

# 终端 3 — Celery Worker（可选）
cd backend && uv run celery -A config worker --loglevel=info
```

### 常用命令

#### 前端

```bash
npm run dev        # 启动开发服务器
npm run build      # 生产环境构建
npm run preview    # 预览生产构建
npm run lint       # 运行 ESLint
```

#### 后端

```bash
uv run python manage.py runserver          # 启动开发服务器
uv run python manage.py makemigrations     # 创建数据库迁移
uv run python manage.py migrate            # 执行迁移
uv run python manage.py createsuperuser    # 创建管理员
uv run pytest                              # 运行测试
uv run black .                             # 代码格式化
uv run flake8                              # 代码风格检查
```

### API 文档

后端运行后访问：

- **Swagger UI**：http://localhost:8000/api/docs/
- **OpenAPI Schema**：http://localhost:8000/api/schema/

## 环境变量

### 后端（`backend/.env`）

从示例文件复制并按需修改：

```bash
cp backend/.env.example backend/.env
```

主要变量：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `SECRET_KEY` | Django 密钥 | *（生产环境需更改）* |
| `DEBUG` | 调试模式 | `True` |
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://postgres:postgres@localhost:5432/monkeyui_dev` |
| `CELERY_BROKER_URL` | Celery 使用的 Redis 地址 | `redis://localhost:6379/0` |
| `DEFAULT_LLM_PROVIDER` | LLM 提供商（`gemini`、`openrouter`、`qwen`） | — |
| `FILE_STORAGE_BACKEND` | 存储后端（`local` 或 `s3`） | `local` |

完整变量列表（包括 LLM 和 S3 配置）请参阅 [`backend/.env.example`](backend/.env.example)。

### 前端（`frontend/.env`）

```
VITE_API_URL=http://localhost:8000/api
```

## 国际化（i18n）

项目支持**英文**（默认）和**中文**。

### 前端

- 翻译文件位置：`frontend/public/locales/{en,zh}/translation.json`
- 使用 `react-i18next` 的 `t()` 函数——切勿硬编码面向用户的文本。

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('welcome.title')}</h1>;
}
```

### 后端

- 使用 `gettext_lazy()` 标记字符串：

```python
from django.utils.translation import gettext_lazy as _
message = _("Hello, world!")
```

- 生成并编译翻译文件：

```bash
uv run python manage.py makemessages -l zh_Hans
uv run python manage.py compilemessages
```

## 部署

项目包含多阶段 `Dockerfile` 和 `fly.toml` 配置，支持部署到 [Fly.io](https://fly.io)。

```bash
# 部署到 Fly.io
fly deploy
```

## 常见问题

| 问题 | 解决方案 |
|---|---|
| 数据库连接错误 | 确保 PostgreSQL 正在运行（macOS：`brew services start postgresql`）。检查 `backend/.env` 中的凭据。 |
| 前端构建错误 | 清除缓存：`rm -rf node_modules && npm install`。检查 Node.js 版本（`node --version`，需要 18+）。 |
| 后端导入错误 | 确保已安装依赖：`cd backend && uv sync`。 |
| Celery 任务未执行 | 确保 Redis 正在运行，且 `backend/.env` 中的 `CELERY_BROKER_URL` 配置正确。 |

## 贡献

提交 Pull Request 前，请先阅读我们的[贡献指南](CONTRIBUTING.md)。

## 文档

- [快速开始指南](QUICKSTART.md)
- [项目结构](PROJECT_STRUCTURE.md)
- [前端文档](frontend/README.md)
- [后端文档](backend/README.md)
- [详细文档](docs/README.md)

## 许可证

[MIT](LICENSE)
