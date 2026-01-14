# AICreate 项目本地部署指南

本指南将帮助您在本地环境中完整部署 AICreate 项目，包括所有依赖服务。

## 📋 目录

- [系统要求](#系统要求)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [服务管理](#服务管理)
- [常见问题](#常见问题)

---

## 🔧 系统要求

### 必需软件

- **Windows 10/11** (本指南针对Windows)
- **Node.js** 18+ 或 20+
  - 下载: https://nodejs.org/
- **Python** 3.13+
  - 下载: https://www.python.org/
  - ⚠️ 安装时勾选 "Add Python to PATH"
- **Git**
  - 下载: https://git-scm.com/

### 可选软件

- **PM2** (进程管理器，自动安装)
- **PostgreSQL** (已集成在项目中)
- **Redis** (已集成在项目中)

---

## 📁 项目结构

```
aicreate_v2/
├── backend/                    # Python FastAPI 后端
│   ├── app/                   # 应用核心代码
│   ├── .env                   # 后端环境变量
│   └── pyproject.toml         # Python 依赖
│
├── frontend/                   # Vue 3 前端应用
│   ├── src/                   # 源代码
│   ├── .env                   # 前端环境变量
│   └── package.json           # Node.js 依赖
│
├── rsshub/                     # RSSHub 本地部署
│   ├── lib/                   # RSSHub 核心库
│   ├── dist/                  # 构建输出
│   ├── .env                   # RSSHub 配置
│   └── package.json           # 依赖管理
│
├── postgresql-18.1-2-windows-x64-binaries/  # PostgreSQL 集成
│   └── pgsql/                 # PostgreSQL 二进制文件
│
├── redis_win32/                # Redis 集成
│   └── redis-server.exe       # Redis 服务器
│
├── postgres_data/              # PostgreSQL 数据目录
│
├── .venv/                      # Python 虚拟环境
│
├── start-all.bat               # ⭐ 一键启动所有服务
├── stop-all.bat                # ⭐ 停止所有服务
├── start-rsshub-native.bat     # 启动 RSSHub
├── stop-rsshub-native.bat      # 停止 RSSHub
├── start-postgres.bat          # 启动 PostgreSQL
├── stop-postgres.bat           # 停止 PostgreSQL
├── start-redis.bat             # 启动 Redis
│
└── LOCAL_SETUP_GUIDE.md        # 本文档
```

---

## 🚀 快速开始

### 方法一：一键启动（推荐）

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd aicreate_v2
   ```

2. **运行一键启动脚本**
   ```bash
   start-all.bat
   ```

   此脚本会自动：
   - ✅ 初始化并启动 PostgreSQL
   - ✅ 启动 Redis
   - ✅ 启动 RSSHub
   - ✅ 启动后端服务
   - ✅ 启动前端服务
   - ✅ 打开浏览器

3. **访问应用**
   - 前端: http://localhost:5173
   - API文档: http://localhost:7002/docs
   - RSSHub: http://localhost:1200

### 方法二：分步启动

如果需要单独控制各个服务：

#### 1. 启动 PostgreSQL

```bash
# 首次使用需要初始化
init-postgres.bat

# 启动 PostgreSQL
start-postgres.bat
```

#### 2. 启动 Redis

```bash
start-redis.bat
```

#### 3. 启动 RSSHub

```bash
# 首次使用需要构建
cd rsshub
npm install
npm run build
cd ..

# 启动 RSSHub
start-rsshub-native.bat
```

#### 4. 启动后端

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖（首次）
cd backend
pip install -r requirements.txt

# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 7002 --reload
```

#### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ 详细配置

### 环境变量配置

#### 后端配置 ([backend/.env](backend/.env))

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/aicreate

# Redis
REDIS_URL=redis://localhost:6381/0

# API 配置
API_HOST=0.0.0.0
API_PORT=7002

# RSSHub（本地部署）
RSSHUB_INSTANCE=http://localhost:1200

# LLM 提供商
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
ZHIPUAI_API_KEY=your-zhipuai-api-key
ZHIPUAI_MODEL=glm-4

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

#### 前端配置 ([frontend/.env](frontend/.env))

```env
VITE_API_URL=http://localhost:7002/api/v1
VITE_WS_URL=ws://localhost:7002/api/v1/ws
```

#### RSSHub 配置 ([rsshub/.env](rsshub/.env))

```env
NODE_ENV=production
PORT=1200

# 缓存配置（使用项目内的 Redis）
CACHE_TYPE=redis
REDIS_URL=redis://localhost:6381/0
CACHE_EXPIRE=300

# 网络配置
REQUEST_RETRY=3
REQUEST_TIMEOUT=10000

# 日志配置
LOGGER_LEVEL=info
DEBUG_INFO=false
```

### 依赖服务配置

#### PostgreSQL

- **版本**: PostgreSQL 18.1
- **端口**: 5432 (内部) / 5434 (外部，如需要)
- **数据目录**: `postgres_data/`
- **用户**: postgres
- **数据库**: aicreate
- **密码**: postgres (默认，可修改)

**配置文件**: `postgres_data/postgresql.conf`

#### Redis

- **版本**: Redis Win32
- **端口**: 6381
- **配置文件**: `redis_win32/redis.windows.conf`
- **持久化**: 已禁用（开发环境）

**修改端口**: 编辑 `redis.windows.conf` 中的 `port` 配置

#### RSSHub

- **版本**: Latest (从 GitHub 克隆)
- **端口**: 1200
- **进程管理**: PM2
- **缓存**: Redis (localhost:6381)

**更新 RSSHub**:
```bash
cd rsshub
git pull
npm install
npm run build
```

---

## 🎛️ 服务管理

### 启动服务

| 服务 | 脚本 | 说明 |
|------|------|------|
| **所有服务** | `start-all.bat` | 一键启动所有服务 |
| **PostgreSQL** | `start-postgres.bat` | 启动数据库 |
| **Redis** | `start-redis.bat` | 启动缓存 |
| **RSSHub** | `start-rsshub-native.bat` | 启动 RSS 服务 |
| **后端** | 手动启动 | 见"分步启动" |
| **前端** | 手动启动 | 见"分步启动" |

### 停止服务

```bash
# 停止所有服务
stop-all.bat

# 单独停止 RSSHub
stop-rsshub-native.bat

# 单独停止 PostgreSQL
stop-postgres.bat

# 单独停止 Redis（关闭窗口或 Ctrl+C）
```

### 查看服务状态

#### PostgreSQL
```bash
cd postgresql-18.1-2-windows-x64-binaries\pgsql\bin
pg_ctl.exe status -D ..\..\..\postgres_data
```

#### Redis
```bash
cd redis_win32
redis-cli.exe ping
# 返回 PONG 表示正在运行
```

#### RSSHub (PM2)
```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs rsshub

# 查看详细信息
pm2 describe rsshub
```

#### 后端
访问: http://localhost:7002/health

#### 前端
访问: http://localhost:5173

### 重启服务

#### RSSHub
```bash
pm2 restart rsshub
```

#### 后端/前端
在对应的命令行窗口中按 `Ctrl+C` 停止，然后重新运行启动命令。

---

## 🐛 常见问题

### 1. 端口冲突

**问题**: 端口已被占用

**解决**:
```bash
# 查看端口占用
netstat -ano | findstr :7002
netstat -ano | findstr :1200
netstat -ano | findstr :6381
netstat -ano | findstr :5432

# 结束占用进程（替换 <PID>）
taskkill /F /PID <PID>
```

### 2. PostgreSQL 启动失败

**问题**: PostgreSQL 无法启动

**解决方案**:

1. 检查数据目录是否存在
   ```bash
   dir postgres_data
   ```

2. 如果不存在，重新初始化
   ```bash
   init-postgres.bat
   ```

3. 查看日志
   ```bash
   type postgres_data\postgresql.log
   ```

4. 检查端口 5432 是否被占用
   ```bash
   netstat -ano | findstr :5432
   ```

### 3. Redis 启动失败

**问题**: Redis 无法启动

**解决方案**:

1. 检查配置文件
   ```bash
   type redis_win32\redis.windows.conf
   ```

2. 手动启动查看错误
   ```bash
   cd redis_win32
   redis-server.exe redis.windows.conf
   ```

3. 检查端口 6381 是否被占用

### 4. RSSHub 启动失败

**问题**: RSSHub 无法启动

**解决方案**:

1. 检查 Node.js 版本
   ```bash
   node --version
   # 需要 18+ 或 20+
   ```

2. 检查是否已构建
   ```bash
   dir rsshub\dist\index.mjs
   ```

3. 如果未构建，构建 RSSHub
   ```bash
   cd rsshub
   npm install
   npm run build
   ```

4. 查看 PM2 日志
   ```bash
   pm2 logs rsshub
   ```

5. 检查 Redis 是否正在运行
   ```bash
   cd redis_win32
   redis-cli.exe ping
   ```

### 5. 后端启动失败

**问题**: 后端无法启动

**解决方案**:

1. 检查 Python 版本
   ```bash
   python --version
   # 需要 3.13+
   ```

2. 检查虚拟环境
   ```bash
   dir .venv\Scripts\activate.bat
   ```

3. 激活虚拟环境并安装依赖
   ```bash
   .venv\Scripts\activate
   cd backend
   pip install -r requirements.txt
   ```

4. 检查数据库连接
   ```bash
   # 测试 PostgreSQL 连接
   cd postgresql-18.1-2-windows-x64-binaries\pgsql\bin
   psql.exe -U postgres -d aicreate -c "SELECT 1;"
   ```

5. 检查环境变量
   ```bash
   type backend\.env
   ```

### 6. 前端启动失败

**问题**: 前端无法启动

**解决方案**:

1. 检查 Node.js 版本
   ```bash
   node --version
   npm --version
   ```

2. 删除 node_modules 并重新安装
   ```bash
   cd frontend
   rmdir /s /q node_modules
   del package-lock.json
   npm install
   ```

3. 检查端口 5173 是否被占用
   ```bash
   netstat -ano | findstr :5173
   ```

### 7. PM2 相关问题

**问题**: PM2 命令不可用

**解决**:
```bash
# 全局安装 PM2
npm install -g pm2

# 验证安装
pm2 --version
```

**问题**: RSSHub 实例损坏

**解决**:
```bash
# 完全清除 RSSHub 实例
pm2 delete rsshub
pm2 flush
pm2 save --force

# 重新启动
start-rsshub-native.bat
```

### 8. 数据库迁移问题

**问题**: 数据库表不存在或结构错误

**解决**:
```bash
# 激活虚拟环境
.venv\Scripts\activate

# 运行数据库迁移
cd backend
alembic upgrade head
```

---

## 📦 依赖服务版本

| 服务 | 版本 | 用途 |
|------|------|------|
| **PostgreSQL** | 18.1 | 主数据库 |
| **Redis** | 7.x (Win32) | 缓存 / RSSHub 缓存 |
| **RSSHub** | Latest | RSS 生成服务 |
| **Node.js** | 18+ / 20+ | 前端 / RSSHub |
| **Python** | 3.13+ | 后端 |
| **PM2** | Latest | RSSHub 进程管理 |

---

## 🔒 安全建议

### 生产环境部署

1. **修改默认密码**
   - PostgreSQL 密码
   - RSSHub ACCESS_KEY

2. **配置防火墙**
   - 仅开放必要端口
   - 限制数据库访问

3. **使用环境变量**
   - 不要在代码中硬编码密钥
   - 使用 `.env` 文件（不提交到 Git）

4. **启用 HTTPS**
   - 使用 Nginx 或 Caddy
   - 配置 SSL 证书

5. **定期备份**
   - PostgreSQL 数据库
   - Redis 持久化（如启用）

---

## 📝 开发提示

### 后端开发

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 运行测试
cd backend
pytest

# 代码格式化
black .
isort .

# 类型检查
mypy .
```

### 前端开发

```bash
cd frontend

# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 运行测试
npm run test
```

### RSSHub 开发

```bash
cd rsshub

# 开发模式
npm run dev

# 构建
npm run build

# 测试
npm test
```

---

## 🆘 获取帮助

如果遇到问题：

1. 查看服务日志
2. 检查端口占用
3. 验证环境变量配置
4. 查看本文档的"常见问题"部分

---

## 📄 许可证

本项目遵循相应的开源许可证。详见各子项目的 LICENSE 文件。

---

## 🎉 完成！

现在您已经成功部署了 AICreate 项目的所有服务！

**下一步**:
- 访问 http://localhost:5173 开始使用
- 查看 API 文档: http://localhost:7002/docs
- 探索 RSSHub: http://localhost:1200

**提示**: 首次启动可能需要较长时间，请耐心等待。

如有任何问题，请参考"常见问题"部分或联系项目维护者。

---

*最后更新: 2025-01-15*
