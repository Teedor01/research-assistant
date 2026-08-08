import json
import logging
from typing import Type, TypeVar
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError

from app.providers.llm.base import (
    LLMProvider, ModelTier, LLMResponse, TokenUsage, StructuredLLMResponse,
)
from pydantic import BaseModel, ValidationError
import asyncio

from app.providers.llm.base import (
    LLMProvider, ModelTier, LLMResponse, TokenUsage,
)
from app.core.config import Settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

RETRYABLE_EXCEPTIONS = (APIError, APITimeoutError, RateLimitError)


class RequestyLLMProvider(LLMProvider):
    """Requesty implementation of LLMProvider. This is the ONLY file in the
    codebase that should import the openai SDK... everything else depends on
    LLMProvider, not on Requesty or OpenAI specifically."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = AsyncOpenAI(
            api_key=settings.requesty_api_key,
            base_url=settings.requesty_base_url,
            timeout=settings.llm_request_timeout_seconds,
        )
        self._model_map = {
            ModelTier.FAST: settings.llm_model_fast,
            ModelTier.REASONING: settings.llm_model_reasoning,
        }

    def _resolve_model(self, tier: ModelTier) -> str:
        return self._model_map[tier]

    async def _call_with_retries(self, **kwargs) -> "openai.types.chat.ChatCompletion":
        max_retries = self._settings.llm_max_retries
        base_delay = self._settings.llm_retry_base_delay_seconds

        last_exception: Exception | None = None
        for attempt in range(max_retries):
            try:
                return await self._client.chat.completions.create(**kwargs)
            except RETRYABLE_EXCEPTIONS as e:
                last_exception = e
                delay = base_delay * (2 ** attempt)  # exponential backoff
                logger.warning(
                    "Requesty call failed (attempt %d/%d): %s. Retrying in %.1fs",
                    attempt + 1, max_retries, e, delay,
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
        raise RuntimeError(f"Requesty call failed after {max_retries} attempts") from last_exception

    def _extract_usage(self, completion) -> TokenUsage:
        usage = completion.usage
        return TokenUsage(
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        model = self._resolve_model(tier)
        completion = await self._call_with_retries(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = completion.choices[0]
        return LLMResponse(
            text=choice.message.content or "",
            tokens_used=self._extract_usage(completion),
            model=model,
            finish_reason=choice.finish_reason,
        )

    

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.0,
        max_tokens: int = 4000,
    ) -> StructuredLLMResponse[T]:
        model = self._resolve_model(tier)
        schema_hint = json.dumps(response_model.model_json_schema(), indent=2)
        full_system_prompt = (
            f"{system_prompt}\n\n"
            f"Respond with ONLY a JSON object matching this schema, no other text, "
            f"no markdown fences:\n{schema_hint}\n\n"
            f"IMPORTANT: Your response must be a direct instance of this schema. "
            f"Do NOT include schema-structure keys like \"$defs\", \"properties\", "
            f"\"required\", or \"type\" in your response. Only include the actual "
            f"field names (e.g. \"simple_explanation\", \"core_concepts\") with real "
            f"values filled in directly, as a flat JSON object."
        )

        completion = await self._call_with_retries(
            model=model,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens = max_tokens,
        )
        choice = completion.choices[0]
        raw = choice.message.content or ""

        try:
            parsed = self._parse_json_defensively(raw)
            data = response_model.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(
                "Structured generation failed to parse for model=%s. Raw output: %r",
                response_model.__name__, raw[:500],
            )
            raise ValueError(
                f"LLM returned invalid structured output for {response_model.__name__}"
            ) from e

        return StructuredLLMResponse(
            data=data,
            tokens_used=self._extract_usage(completion),
            model=model,
            finish_reason=choice.finish_reason,
        )


    @staticmethod
    def _parse_json_defensively(raw: str) -> dict:
        """Free/weaker models via Requesty often wrap JSON in markdown fences
        despite instructions not to. Strip defensively before parsing."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())