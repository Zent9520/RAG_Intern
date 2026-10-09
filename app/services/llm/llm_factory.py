from app.services.llm.ollama_service import (
    OllamaService
)

from app.services.llm.openai_service import (
    OpenAIService
)


class LLMFactory:

    @staticmethod
    def create():

        return (
            OllamaService()
        )

    @staticmethod
    def create_openai(

        model: str =
        "gpt-4.1-mini"

    ):

        return (
            OpenAIService(
                model=model
            )
        )