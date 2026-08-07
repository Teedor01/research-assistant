from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncIterator, Generic, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ModelTier(str, Enum):
    FAST = "fast"
    REASONING = "reasoning"


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    text: str
    tokens_used: TokenUsage
    model: str
    finish_reason: Optional[str] = None


class StructuredLLMResponse(BaseModel, Generic[T]):
    data: T
    tokens_used: TokenUsage
    model: str
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    @abstractmethod
    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.0,
    ) -> StructuredLLMResponse[T]:
        """Returns data + metadata. Provider does NOT log token usage itself —
        that's an observability concern, handled by the caller/node via
        observed_node, keeping provider responsibilities limited to talking
        to the LLM and returning what happened."""
        ...

    async def stream_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        raise NotImplementedError("Streaming not yet implemented")
        yield  # pragma: no cover

    async def generate_from_content(
        self,
        *,
        system_prompt: str,
        content_blocks: list[dict],
        tier: ModelTier = ModelTier.REASONING,
    ) -> LLMResponse:
        raise NotImplementedError("Multimodal generation not yet implemented")