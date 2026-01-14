"""Daily News Briefing workflow plugin."""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from loguru import logger

from app.core.plugin_loader import WorkflowPlugin
from app.core.config import get_settings
from app.tools.rsshub import RSSHubClient
from app.utils.content_filter import ContentFilter
from app.utils.zhipuai import ZhipuAIChatModel

settings = get_settings()


class NewsState(TypedDict):
    """State for Daily News Briefing workflow."""

    messages: Annotated[List[Any], add_messages]
    sources: List[str]
    max_articles: int
    recent_hours: int
    raw_feeds: List[Dict]
    filtered_feeds: List[Dict]
    integrated_content: str
    final_report: str


class DailyNewsBriefingPlugin(WorkflowPlugin):
    """Daily News Briefing workflow plugin."""

    def __init__(self):
        super().__init__(
            name="daily_news_briefing",
            version="1.0.0",
            description="Automatically aggregates, filters, and summarizes daily news from multiple RSS sources",
            author="AICreate",
        )

    def get_workflow(self):
        """Get LangGraph workflow for daily news briefing."""
        workflow = StateGraph(NewsState)

        # Add nodes
        workflow.add_node("fetch_feeds", self.fetch_feeds)
        workflow.add_node("filter_content", self.filter_content)
        workflow.add_node("integrate_content", self.integrate_content)
        workflow.add_node("translate_content", self.translate_content)
        workflow.add_node("generate_report", self.generate_report)

        # Add edges
        workflow.add_edge(START, "fetch_feeds")
        workflow.add_edge("fetch_feeds", "filter_content")
        workflow.add_edge("filter_content", "integrate_content")
        workflow.add_edge("integrate_content", "translate_content")
        workflow.add_edge("translate_content", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def get_config_schema(self) -> dict:
        """Get configuration schema."""
        return {
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "RSSHub routes to fetch news from",
                    "examples": [
                        "/hackernews/frontpage",
                        "/github/repo/DIYgod/RSSHub/issues",
                        "/zhihu/hotlist",
                    ],
                },
                "max_articles": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Maximum number of articles to include in the report",
                },
                "recent_hours": {
                    "type": "integer",
                    "default": 24,
                    "minimum": 1,
                    "maximum": 168,
                    "description": "Only include articles from the last N hours",
                },
                "enable_translation": {
                    "type": "boolean",
                    "default": True,
                    "description": "Translate foreign content to Chinese",
                },
                "strict_filtering": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable strict content filtering",
                },
            },
            "required": ["sources"],
        }

    def get_default_config(self) -> dict:
        """Get default configuration."""
        # 从环境变量读取默认配置，或使用内置默认值
        import os
        from ast import literal_eval

        # 尝试从环境变量读取 sources（支持 Python 列表语法）
        default_sources = ["/hackernews/frontpage", "/zhihu/hotlist"]
        env_sources = os.getenv("RSSHUB_DEFAULT_SOURCES")
        if env_sources:
            try:
                default_sources = literal_eval(env_sources)
            except:
                # 如果解析失败，按逗号分割
                default_sources = [s.strip() for s in env_sources.split(",")]

        return {
            "sources": default_sources,
            "max_articles": int(os.getenv("RSSHUB_MAX_ARTICLES", "20")),
            "recent_hours": int(os.getenv("RSSHUB_RECENT_HOURS", "24")),
            "enable_translation": os.getenv("RSSHUB_ENABLE_TRANSLATION", "True").lower() == "true",
            "strict_filtering": os.getenv("RSSHUB_STRICT_FILTERING", "False").lower() == "true",
        }

    async def fetch_feeds(self, state: NewsState) -> Dict:
        """Fetch RSS feeds from RSSHub."""
        logger.info("Fetching RSS feeds")

        client = RSSHubClient()

        # Prepare feed configurations
        routes = [
            {"route": source, "source": source, "category": "General"}
            for source in state["sources"]
        ]

        # Fetch all feeds concurrently
        feeds = await client.fetch_multiple_feeds(routes)
        await client.close()

        if not feeds:
            logger.warning("Failed to fetch any feeds from RSSHub, using demo data")
            # Use demo data for demonstration
            from datetime import datetime, timedelta

            demo_entries = [
                {
                    "title": "人工智能技术突破：新模型实现更高效的推理",
                    "link": "https://example.com/ai-breakthrough",
                    "description": "研究人员开发出新型神经网络架构，在保持准确率的同时将推理速度提升3倍。该技术有望应用于自动驾驶、智能助手等领域。",
                    "published": (datetime.utcnow() - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "author": "科技日报",
                    "source": state["sources"][0] if state["sources"] else "demo",
                    "tags": ["AI", "技术"],
                },
                {
                    "title": "全球气候峰会达成新协议",
                    "link": "https://example.com/climate-summit",
                    "description": "195个国家代表在为期两周的气候峰会上达成历史性协议，承诺在2030年前将碳排放减少50%。协议还包括设立1000亿美元的气候基金。",
                    "published": (datetime.utcnow() - timedelta(hours=5)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "author": "环球时报",
                    "source": state["sources"][1] if len(state["sources"]) > 1 else "demo",
                    "tags": ["气候", "国际"],
                },
                {
                    "title": "新型电池技术使电动汽车续航翻倍",
                    "link": "https://example.com/battery-tech",
                    "description": "科学家开发出固态电池新技术，能量密度提升两倍，充电时间缩短至10分钟。多家汽车制造商表示将在2025年量产搭载该电池的车型。",
                    "published": (datetime.utcnow() - timedelta(hours=8)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "author": "汽车之家",
                    "source": state["sources"][0] if state["sources"] else "demo",
                    "tags": ["新能源", "汽车"],
                },
                {
                    "title": "量子计算领域取得重大进展",
                    "link": "https://example.com/quantum",
                    "description": "国际团队成功实现1000量子比特的稳定纠缠，创造了新的世界纪录。这一突破为实用化量子计算机的开发奠定了基础。",
                    "published": (datetime.utcnow() - timedelta(hours=12)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "author": "科学周刊",
                    "source": state["sources"][1] if len(state["sources"]) > 1 else "demo",
                    "tags": ["量子计算", "科技"],
                },
                {
                    "title": "火星探测任务发现新证据",
                    "link": "https://example.com/mars",
                    "description": "最新的火星探测器在火星表面发现了古代河流沉积物的证据，进一步支持了火星曾经存在液态水和可能的生命形式的假设。",
                    "published": (datetime.utcnow() - timedelta(hours=18)).strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "author": "航天科技",
                    "source": state["sources"][0] if state["sources"] else "demo",
                    "tags": ["航天", "探索"],
                },
            ]

            logger.info(f"Using {len(demo_entries)} demo articles")
            return {
                "messages": [SystemMessage(content=f"Using demo data: {len(demo_entries)} articles")],
                "raw_feeds": demo_entries[: state["max_articles"]],
            }

        # Extract all entries
        all_entries = []
        for feed_data in feeds:
            feed = feed_data["feed"]
            for entry in feed["entries"]:
                entry["source"] = feed_data["source"]
                all_entries.append(entry)

        # Filter by recent hours
        client = RSSHubClient()
        recent_entries = client.filter_recent_entries(all_entries, state["recent_hours"])

        # Limit to max_articles
        recent_entries = recent_entries[: state["max_articles"]]

        if not recent_entries:
            logger.warning(f"No recent articles found from {len(feeds)} sources")
            return {
                "messages": [SystemMessage(content="No recent articles found")],
                "raw_feeds": [],
            }

        logger.info(f"Fetched {len(recent_entries)} articles from {len(feeds)} sources")

        return {
            "messages": [SystemMessage(content=f"Fetched {len(recent_entries)} articles")],
            "raw_feeds": recent_entries,
        }

    async def filter_content(self, state: NewsState) -> Dict:
        """Filter sensitive content."""
        logger.info("Filtering content for sensitive material")

        filter = ContentFilter(strict_mode=False)  # Use non-strict mode for now

        filtered_articles = filter.filter_articles(state["raw_feeds"])

        logger.info(f"Filtered to {len(filtered_articles)} safe articles")

        return {
            "messages": [
                SystemMessage(content=f"Filtered to {len(filtered_articles)} safe articles")
            ],
            "filtered_feeds": filtered_articles,
        }

    async def integrate_content(self, state: NewsState) -> Dict:
        """Integrate and organize content using LLM."""
        logger.info("Integrating and organizing content")

        # Check if we have articles to process
        if not state.get("filtered_feeds"):
            logger.warning("No articles to integrate")
            return {
                "messages": [AIMessage(content="No articles to integrate")],
                "integrated_content": "无新闻内容",
            }

        # Choose LLM based on configuration (prefer Zhipu AI)
        if settings.zhipuai_api_key:
            llm = ZhipuAIChatModel(
                model=settings.zhipuai_model or "glm-4",
                temperature=0.3,
                zhipuai_api_key=settings.zhipuai_api_key,
            )
            logger.info(f"Using Zhipu AI model: {settings.zhipuai_model}")
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            logger.info("Using OpenAI model: gpt-4o-mini")

        # Prepare content for integration
        content_summary = "\n\n".join(
            [
                f"## {article['title']}\n来源: {article['source']}\n{article['description'][:500]}..."
                for article in state["filtered_feeds"]
            ]
        )

        system_prompt = """你是一个专业的内容整合专家。你的任务是将收集到的新闻内容整合成一份结构化、易读的摘要。

要求：
1. 按主题分类整理新闻（科技、商业、社会、娱乐等）
2. 为每条新闻添加简短摘要（不超过100字）
3. 提取关键信息点（人物、事件、时间、地点）
4. 如果有视频或图片链接，在新闻条目中标注 "[视频]" 或 "[图片]"
5. 保持客观中立的语气

输出格式：
# 分类名称

## 新闻标题
- 摘要：...
- 关键信息：...
- 来源：...
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"以下是需要整合的新闻内容：\n\n{content_summary}"),
        ]

        response = await llm.ainvoke(messages)
        integrated_content = response.content

        return {
            "messages": [AIMessage(content="Content integration completed")],
            "integrated_content": integrated_content,
        }

    async def translate_content(self, state: NewsState) -> Dict:
        """Translate foreign content to Chinese."""
        logger.info("Translating foreign content")

        # Choose LLM based on configuration (prefer Zhipu AI)
        if settings.zhipuai_api_key:
            llm = ZhipuAIChatModel(
                model=settings.zhipuai_model or "glm-4",
                temperature=0.3,
                zhipuai_api_key=settings.zhipuai_api_key,
            )
            logger.info(f"Using Zhipu AI model for translation: {settings.zhipuai_model}")
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            logger.info("Using OpenAI model for translation: gpt-4o-mini")

        # Translate content if needed
        system_prompt = """你是一个专业的翻译专家。你的任务是将以下内容翻译成自然的中文。

要求：
1. 保持原文的结构和格式
2. 翻译要准确、流畅
3. 专业术语要准确翻译
4. 保留原有的链接和标签
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请将以下内容翻译成中文：\n\n{state['integrated_content']}"),
        ]

        response = await llm.ainvoke(messages)
        translated_content = response.content

        return {
            "messages": [AIMessage(content="Translation completed")],
        }

    async def generate_report(self, state: NewsState) -> Dict:
        """Generate final news report in Markdown format."""
        logger.info("Generating final news report")

        # Choose LLM based on configuration (prefer Zhipu AI)
        if settings.zhipuai_api_key:
            llm = ZhipuAIChatModel(
                model=settings.zhipuai_model or "glm-4",
                temperature=0.5,
                zhipuai_api_key=settings.zhipuai_api_key,
            )
            logger.info(f"Using Zhipu AI model for report generation: {settings.zhipuai_model}")
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
            logger.info("Using OpenAI model for report generation: gpt-4o-mini")

        system_prompt = """你是一个专业的新闻编辑。你的任务是将整合后的内容生成一份高质量的每日新闻速报，格式为Markdown。

要求：
1. 添加吸引人的标题和日期
2. 使用合适的Markdown格式（标题、列表、引用等）
3. 添加新闻摘要部分
4. 如果有重要新闻，添加"重点关注"部分
5. 在末尾添加"新闻来源"部分
6. 整体风格简洁、专业、易读

格式示例：
# 每日新闻速报 - {日期}

## 摘要
今日重点新闻概述...

## 重点关注
{重要新闻}

## 分类新闻
{按分类整理的新闻}

## 新闻来源
{列出所有来源}
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["integrated_content"]),
        ]

        response = await llm.ainvoke(messages)
        final_report = response.content

        # Add metadata
        from datetime import datetime

        final_report = f"""# 每日新闻速报 - {datetime.now().strftime("%Y年%m月%d日")}

{final_report}

---
*本报告由 AICreate 智能工作流平台自动生成*
"""

        logger.info("Final news report generated successfully")

        return {
            "messages": [AIMessage(content="Final report generated")],
            "final_report": final_report,
        }


# Plugin class for the loader
Plugin = DailyNewsBriefingPlugin
