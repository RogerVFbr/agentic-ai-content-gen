from crosscutting.logging.app_logger import AppLogger
from openai import OpenAI

class ImageGenerationRepository:

    def __init__(self,
                 logger: AppLogger):

        self._logger = logger
        self._client = OpenAI()

    async def generate(self, prompt: str) -> str:
        self._logger.debug(f"Generating image with prompt: '{prompt}' ...")
        result = self._client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            # size="1024x1024"
        )

        return result.data[0].url