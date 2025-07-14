import base64
import os
from datetime import datetime
from openai import OpenAI
from typing import Any

from configurations.configs import Configs
from crosscutting.logging.app_logger import AppLogger


class ImageRepository:

    def __init__(self,
                 configs: Configs,
                 logger: AppLogger):

        self._configs = configs
        self._logger = logger
        self._client = OpenAI()

    async def generate_image(self, prompt: str) -> tuple[str | None, Any]:
        if not self._configs.flags.enable_image_generation:
            self._logger.warn("Image generation is disabled by configuration. Returning default image id.")
            return None, 'image_generation_disabled'

        self._logger.debug("Generating image ...")

        try:
            response = self._client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                tools=[{"type": "image_generation"}],
            )

            self._logger.debug("Verifying image tool usage ...")

            image_data = [
                output.result
                for output in response.output
                if output.type == "image_generation_call"
            ]

            output_dir = os.path.join(os.path.dirname(__file__), f"..{self._configs.image_generation.deliverables_path}")
            os.makedirs(output_dir, exist_ok=True)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"{current_time}.png")

            if image_data:
                self._logger.debug("Image data found. Saving ...")
                image_base64 = image_data[0]
                with open(output_file, "wb") as f:
                    f.write(base64.b64decode(image_base64))
            else:
                raise ValueError("No image data found in the response.")

            return None, current_time
        except Exception as e:
            self._logger.error(f"Error generating image: {e}", exception=e)
            return None, None
