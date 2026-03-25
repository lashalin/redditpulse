import google.generativeai as genai
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

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"[LLM Error: {str(e)}]"


def get_llm_provider() -> LLMProvider:
    """Factory function - change this to swap LLM providers."""
    return GeminiProvider(model_name="gemini-2.5-flash")
