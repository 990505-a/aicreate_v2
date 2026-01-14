# AICreate 智能工作流平台

高可用、易扩展的智能工作流平台，基于 LangGraph、LangChain 和 DeepAgents 框架构建。

## 功能特性

- 🚀 **高性能架构**：基于 FastAPI 和 Vue 3 的现代化技术栈
- 🔌 **插件系统**：易于扩展的插件架构，支持自定义工作流
- 📊 **实时监控**：WebSocket 实时更新工作流执行状态
- 🛡️ **内容过滤**：多层内容过滤系统（关键词、正则、ML）
- 📰 **RSS 集成**：集成 RSSHub，支持多种数据源
- 🌐 **国际化支持**：自动翻译国外内容为中文
- 📈 **可观测性**：Prometheus 监控和日志记录
- 💻 **本地部署**：完全本地化部署，无需 Docker，开箱即用

## 技术栈

### 后端
- **框架**: FastAPI 0.115+
- **工作流**: LangGraph, LangChain, DeepAgents
- **数据库**: PostgreSQL 16 + SQLAlchemy
- **缓存**: Redis 7
- **监控**: Prometheus

### 前端
- **框架**: Vue 3 + TypeScript
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket

## 快速开始

### 一键启动（推荐）

本项目已完全本地化部署，无需 Docker。所有依赖服务已集成到项目中。

#### Windows 用户

双击运行 `start-all.bat` 文件，或在命令行中执行：

```cmd
start-all.bat
```

此脚本将自动启动所有服务：
- ✅ PostgreSQL 数据库
- ✅ Redis 缓存服务
- ✅ RSSHub RSS 服务
- ✅ AICreate 后端
- ✅ AICreate 前端

### 首次使用

**重要**: 首次使用前需要构建 RSSHub：

```bash
cd rsshub
npm install
npm run build
cd ..
```

然后运行 `start-all.bat` 启动所有服务。

### 访问应用

启动成功后，访问以下地址：

- **前端应用**: http://localhost:5173
- **API 文档**: http://localhost:7002/docs
- **健康检查**: http://localhost:7002/health
- **RSSHub**: http://localhost:1200

### 📖 详细部署指南

对于完整的配置说明、故障排除和开发指南，请查看：

**[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)**

该指南包含：
- ✅ 系统要求和依赖
- ✅ 详细的项目结构说明
- ✅ 分步启动教程
- ✅ 环境变量配置
- ✅ 服务管理命令
- ✅ 常见问题解决方案
- ✅ 开发提示和最佳实践

---

## 项目结构

```
aicreate_v2/
├── backend/              # FastAPI 后端
├── frontend/             # Vue 3 前端
├── rsshub/               # RSSHub 本地部署
├── postgresql-18.1-2-windows-x64-binaries/  # PostgreSQL 集成
├── redis_win32/          # Redis 集成
├── postgres_data/        # PostgreSQL 数据目录
├── .venv/                # Python 虚拟环境
├── start-all.bat         # ⭐ 一键启动所有服务
├── stop-all.bat          # ⭐ 停止所有服务
└── LOCAL_SETUP_GUIDE.md  # 📖 详细部署指南
```

## 服务管理

### 启动服务

```bash
# 启动所有服务
start-all.bat

# 单独启动 PostgreSQL
start-postgres.bat

# 单独启动 Redis
start-redis.bat

# 单独启动 RSSHub
start-rsshub-native.bat
```

### 停止服务

```bash
# 停止所有服务
stop-all.bat

# 单独停止 RSSHub
stop-rsshub-native.bat

# 单独停止 PostgreSQL
stop-postgres.bat
```

## 技术栈

### 后端
- **框架**: FastAPI 0.115+
- **工作流**: LangGraph, LangChain, DeepAgents
- **数据库**: PostgreSQL 18.1
- **缓存**: Redis 7

### 前端
- **框架**: Vue 3 + TypeScript
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket

### RSS 服务
- **RSSHub**: 本地部署版本，使用项目内 Redis 缓存

## 内置工作流

### 每日新闻速报

自动聚合、过滤和总结来自多个 RSS 源的新闻内容。

**功能特性**:
- 从 RSSHub 获取多个新闻源
- 敏感内容过滤（关键词、正则）
- AI 内容整合和优化
- 外国新闻自动翻译
- 图片/视频链接嵌入
- 生成高质量 Markdown 新闻稿

**使用方法**:
1. 在首页选择 "每日新闻速报" 工作流
2. 配置 RSS 源和参数
3. 点击"启动"按钮
4. 实时监控执行进度
5. 查看生成的新闻稿

## 插件开发

创建自定义工作流插件：

```python
from app.core.plugin_loader import WorkflowPlugin
from langgraph.graph import StateGraph

class MyWorkflowPlugin(WorkflowPlugin):
    def __init__(self):
        super().__init__(
            name="my_workflow",
            version="1.0.0",
            description="我的自定义工作流",
            author="Your Name"
        )

    def get_workflow(self):
        """返回 LangGraph 工作流"""
        workflow = StateGraph(dict)

        # 添加节点
        workflow.add_node("step1", self.step1)
        workflow.add_node("step2", self.step2)

        # 添加边
        workflow.add_edge("__start__", "step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", "__end__")

        return workflow.compile()

    def get_config_schema(self):
        """返回配置 schema"""
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"}
            }
        }

    def get_default_config(self):
        """返回默认配置"""
        return {"param1": "default", "param2": 10}

    async def step1(self, state):
        """工作流步骤 1"""
        # 你的逻辑
        return {"output": "result"}

    async def step2(self, state):
        """工作流步骤 2"""
        # 你的逻辑
        return {"output": "final result"}


# 插件类（用于插件加载器）
Plugin = MyWorkflowPlugin
```

将插件文件保存到 `backend/app/plugins/my_workflow_plugin.py`，系统会自动加载。

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 主要 API 端点

- `GET /api/v1/workflows/` - 列出所有工作流
- `GET /api/v1/workflows/{id}` - 获取工作流详情
- `POST /api/v1/workflows/{id}/start` - 启动工作流
- `GET /api/v1/executions/` - 列出执行记录
- `GET /api/v1/executions/{id}` - 获取执行详情
- `POST /api/v1/executions/{id}/cancel` - 取消执行

### WebSocket 端点

- `WS /api/v1/ws/executions/{id}/updates` - 实时执行更新

## 内容过滤

平台内置多层内容过滤系统，确保内容符合中国合规要求。

### 过滤层级

1. **关键词过滤**: 基于预定义的敏感词表
2. **正则过滤**: 使用正则表达式匹配变体
3. **ML 过滤**: 可选的机器学习模型过滤

### 添加自定义过滤

```python
from app.utils.content_filter import ContentFilter

filter = ContentFilter()

# 添加敏感关键词
filter.add_keyword("敏感词")

# 添加正则模式
filter.add_pattern(r"sensitive.*pattern")

# 过滤内容
result = filter.filter_text("需要过滤的文本")
print(result.filtered_content)
```

## 监控和日志

### Prometheus 指标

平台提供以下 Prometheus 指标：

- `workflow_executions_total` - 工作流执行总数
- `workflow_duration_seconds` - 工作流执行时长
- `workflow_retries_total` - 工作流重试次数
- `rsshub_requests_total` - RSSHub 请求总数
- `content_filter_total` - 内容过滤操作总数

### 访问指标

```bash
curl http://localhost:8000/metrics
```

## 测试

### 运行后端测试

```bash
cd backend
pytest

# 带覆盖率
pytest --cov=app --cov-report=html
```

### 运行前端测试

```bash
cd frontend
npm run test
```

## 环境变量

主要环境变量：

| 变量名 | 描述 | 默认值 |
|---------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | - |
| `REDIS_URL` | Redis 连接字符串 | redis://localhost:6381/0 |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `RSSHUB_INSTANCE` | RSSHub 实例 URL | http://localhost:1200 |
| `API_PORT` | API 端口 | 7002 |
| `LOG_LEVEL` | 日志级别 | INFO |

完整环境变量列表请参考 `backend/.env.example`。

## 故障排查

### 常见问题

**1. 数据库连接失败**

```bash
# 检查 PostgreSQL 是否运行
cd postgresql-18.1-2-windows-x64-binaries\pgsql\bin
pg_ctl.exe status -D ..\..\..\postgres_data

# 查看日志
type ..\..\..\postgres_data\postgresql.log
```

**2. LLM API 调用失败**

- 检查 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY` 是否正确设置
- 确保账户有足够的配额

**3. 工作流执行失败**

```bash
# 查看后端日志（在 backend 窗口中）
# 检查 Redis 连接
cd redis_win32
redis-cli.exe ping
# 应该返回 PONG
```

**4. RSSHub 无法访问**

```bash
# 检查 RSSHub 状态
pm2 status

# 查看 RSSHub 日志
pm2 logs rsshub

# 重启 RSSHub
pm2 restart rsshub
```

**更多故障排除方案请查看**: [LOCAL_SETUP_GUIDE.md 的常见问题部分](LOCAL_SETUP_GUIDE.md#常见问题)

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: https://github.com/yourusername/aicreate-workflow-platform
- 问题反馈: https://github.com/yourusername/aicreate-workflow-platform/issues

## 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态ful 工作流编排
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [DeepAgents](https://github.com/langchain-ai/deepagents) - 多智能体系统
- [RSSHub](https://github.com/DIYgod/RSSHub) - 万物皆可 RSS
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Python Web 框架
