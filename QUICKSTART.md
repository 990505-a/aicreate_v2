# 快速开始指南

> 🎉 **恭喜！** 你已经克隆了 AICreate 智能工作流平台

本项目已包含前端依赖，只需要简单的准备即可启动！

---

## 📋 前置要求

在开始之前，请确保已安装以下软件：

### 必需软件

1. **Node.js** 18+ 或 20+
   - 下载：https://nodejs.org/
   - 安装后验证：`node --version`

2. **Python** 3.13+
   - 下载：https://www.python.org/
   - ⚠️ 安装时勾选 **"Add Python to PATH"**
   - 安装后验证：`python --version`

3. **PM2** (进程管理器)
   - 自动安装，无需手动操作

---

## 🚀 三步启动

### 第一步：构建 RSSHub

RSSHub 是项目的核心组件，需要首次构建：

```bash
# Windows 用户
cd rsshub
npm install
npm run build
cd ..
```

**⏱️ 预计时间**：首次安装约 3-5 分钟（取决于网络速度）

**📝 说明**：
- `npm install` - 安装 RSSHub 依赖包
- `npm run build` - 构建 RSSHub 生产版本

---

### 第二步：创建 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..
```

**⏱️ 预计时间**：约 2-3 分钟

---

### 第三步：一键启动所有服务

```bash
# Windows 用户
start-all.bat
```

这个脚本会自动：
1. ✅ 启动 PostgreSQL 数据库
2. ✅ 启动 Redis 缓存服务
3. ✅ 启动 RSSHub 服务
4. ✅ 启动后端 API
5. ✅ 启动前端应用
6. ✅ 自动打开浏览器

**⏱️ 预计时间**：约 1-2 分钟

---

## 🌐 访问应用

启动成功后，会自动打开浏览器，或手动访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端应用** | http://localhost:5173 | 主应用界面 |
| **API 文档** | http://localhost:7002/docs | Swagger 文档 |
| **健康检查** | http://localhost:7002/health | 后端状态 |
| **RSSHub** | http://localhost:1200 | RSS 服务 |

---

## 🛑 停止服务

当不需要使用时，运行：

```bash
stop-all.bat
```

这会停止所有服务（PostgreSQL、Redis、RSSHub、后端、前端）

---

## 🔧 常见问题

### Q1: 提示 "Node.js not found"

**解决方案**：
1. 访问 https://nodejs.org/
2. 下载并安装 LTS 版本
3. 重启命令行窗口
4. 验证：`node --version`

---

### Q2: 提示 "Python not found" 或 "venv Scripts\activate" 找不到

**解决方案**：
1. 访问 https://www.python.org/
2. 下载 Python 3.13+
3. ⚠️ **重要**：安装时勾选 "Add Python to PATH"
4. 重启命令行窗口
5. 验证：`python --version`

---

### Q3: RSSHub 构建失败

**可能原因**：网络问题导致 npm 下载失败

**解决方案**：
```bash
# 清理缓存
cd rsshub
rmdir /s /q node_modules
del package-lock.json

# 使用国内镜像重新安装
npm install --registry=https://registry.npmmirror.com
npm run build
```

---

### Q4: 端口被占用

**错误提示**：`Error: listen EADDRINUSE: address already in use`

**解决方案**：

查看占用进程：
```bash
# 查看端口占用
netstat -ano | findstr :7002
netstat -ano | findstr :1200
netstat -ano | findstr :6381
```

终止进程：
```bash
taskkill /F /PID <进程ID>
```

或直接运行：
```bash
stop-all.bat
```

---

### Q5: PostgreSQL 启动失败

**解决方案**：

```bash
# 重新初始化数据库
rmdir /s /q postgres_data
init-postgres.bat

# 然后重新启动
start-all.bat
```

---

## 📦 项目结构说明

```
aicreate_v2/
├── frontend/              # Vue 3 前端（含 node_modules）
│   ├── node_modules/      # ✅ 已包含，无需安装
│   └── ...
│
├── backend/               # Python 后端
│   └── ...
│
├── rsshub/                # RSSHub 服务（需构建）
│   ├── node_modules/      # ❌ 需要自己安装
│   └── dist/             # ❌ 需要自己构建
│
├── postgresql-* /         # PostgreSQL 集成
├── redis_win32/          # Redis 集成
│
├── start-all.bat         # ⭐ 一键启动
├── stop-all.bat          # ⭐ 停止所有服务
│
└── .venv/                # Python 虚拟环境（需创建）
```

---

## 💡 提示

### 首次启动检查清单

- [ ] Node.js 已安装（18+ 或 20+）
- [ ] Python 已安装（3.13+）
- [ ] RSSHub 已构建（`cd rsshub && npm install && npm run build`）
- [ ] Python 虚拟环境已创建（`python -m venv .venv`）
- [ ] 后端依赖已安装（`cd backend && pip install -r requirements.txt`）

### 日常使用

之后每次使用只需：
```bash
start-all.bat
```

停止服务：
```bash
stop-all.bat
```

---

## 📚 更多文档

- **详细部署指南**：[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)
- **项目说明**：[README.md](README.md)
- **改造记录**：[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)

---

## 🆘 需要帮助？

如果遇到问题：

1. 查看 [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md) 的"常见问题"部分
2. 检查服务日志：
   - Backend：在 backend 窗口中查看
   - Frontend：在 frontend 窗口中查看
   - RSSHub：运行 `pm2 logs rsshub`
3. 检查端口占用：`netstat -ano | findstr :端口号`

---

## 🎉 开始使用

现在你已经准备好启动项目了！

```bash
# 1. 构建 RSSHub（首次使用）
cd rsshub
npm install
npm run build
cd ..

# 2. 创建 Python 虚拟环境（首次使用）
python -m venv .venv
.venv\Scripts\activate
cd backend
pip install -r requirements.txt
cd ..

# 3. 启动所有服务
start-all.bat

# 4. 访问应用
# 浏览器会自动打开 http://localhost:5173
```

**祝使用愉快！** 🚀

---

*最后更新: 2025-01-15*
