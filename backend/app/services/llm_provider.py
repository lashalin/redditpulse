import google.generativeai as genai
from google.generativeai import types
from abc import ABC, abstractmethod
from app.config import get_settings

settings = get_settings()


class LLMProvider(ABC):
    """Abstract LLM provider - swap Gemini for Claude/others later."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini free API provider."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=settings.gemini_api_key)
        # Safety settings - allow all content for brand analysis
        self.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",
            ),
        ]
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=None,
        )
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Gemini API."""
        try:
            # Rebuild model with system instruction if provided
            if system_prompt:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_prompt,
                )
            else:
                model = self.model

            response = model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
            )

            # Handle blocked responses
            if not response.candidates:
                print("Gemini: No candidates returned (blocked)")
                return "分析内容被安全过滤器拦截，请尝试其他关键词。"

            candidate = response.candidates[0]
            if candidate.finish_reason and candidate.finish_reason != 1:
                # finish_reason 1 = STOP (normal), others = blocked/error
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text
                return "分析内容被安全过滤器拦截，请尝试其他关键词。"

            # Normal response
            if hasattr(response, 'text'):
                return response.text

            # Fallback: try to extract from parts
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text

            return "未能生成分析内容，请重试。"

        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"AI分析暂时不可用，请稍后重试。错误详情: {str(e)[:200]}"


def get_llm_provider() -> LLMProvider:
    """Factory function - change this to swap LLM providers."""
    return GeminiProvider(model_name="gemini-2.5-flash")
