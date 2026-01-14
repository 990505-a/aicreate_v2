"""Zhipu AI / BigModel API client for LangChain integration."""

from typing import Optional, List, Any, Dict
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
import httpx
import json
import asyncio

from app.core.config import get_settings

settings = get_settings()


class ZhipuAIClient:
    """Zhipu AI API client."""

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url, timeout=60.0, headers={"Authorization": f"Bearer {api_key}"}
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        Call Zhipu AI chat API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter

        Returns:
            Response dict with 'content' and 'usage'
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            result = response.json()

            # Extract content from response
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})

            return {"content": content, "usage": usage, "model": result.get("model", self.model)}

        except httpx.HTTPStatusError as e:
            raise Exception(f"Zhipu AI API error: {e.response.text}")
        except Exception as e:
            raise Exception(f"Zhipu AI client error: {e}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class ZhipuAIChatModel(BaseChatModel):
    """LangChain integration for Zhipu AI models."""

    model: str = "glm-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    def __init__(
        self,
        model: str = "glm-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        api_key = kwargs.get("zhipuai_api_key") or settings.zhipuai_api_key
        self._client = ZhipuAIClient(api_key=api_key, model=model)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def client(self) -> ZhipuAIClient:
        """Get the ZhipuAI client."""
        return self._client

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs,
    ) -> ChatResult:
        """Generate chat completion using Zhipu AI."""
        # Convert LangChain messages to Zhipu format
        zhipu_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                zhipu_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                zhipu_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                zhipu_messages.append({"role": "system", "content": msg.content})

        # Call API (async, so we need to handle differently)
        result = asyncio.run(
            self.client.chat(
                messages=zhipu_messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
        )

        # Create ChatGeneration
        generation = ChatGeneration(message=AIMessage(content=result["content"]))

        return ChatResult(generations=[generation])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs,
    ) -> ChatResult:
        """Async version of generate."""
        zhipu_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                zhipu_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                zhipu_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                zhipu_messages.append({"role": "system", "content": msg.content})

        result = await self.client.chat(
            messages=zhipu_messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )

        generation = ChatGeneration(message=AIMessage(content=result["content"]))

        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "zhipuai"
