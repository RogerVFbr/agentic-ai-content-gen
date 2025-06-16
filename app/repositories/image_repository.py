import base64

import aiohttp
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from openai import OpenAI
from typing import Any
import textwrap

from configurations.configs import Configs
from crosscutting.logging.app_logger import AppLogger


class ImageRepository:

    def __init__(self,
                 configs: Configs,
                 logger: AppLogger):

        self._configs = configs
        self._logger = logger
        self._client = OpenAI()

    async def generate_advanced(self, prompt: str) -> tuple[str | None, Any]:
        response = self._client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            tools=[{"type": "image_generation"}],
        )

        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]

        # Save the image locally with the current datetime as the filename
        output_dir = os.path.join(os.path.dirname(__file__), f"..{self._configs.image_generation.deliverables_path}")
        os.makedirs(output_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{current_time}.png")

        if image_data:
            image_base64 = image_data[0]
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(image_base64))

        return None, current_time

    async def generate(self, prompt: str) -> tuple[str | None, Any]:
        self._logger.debug(f"Generating image with prompt: '{prompt}' ...")
        result = self._client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=self._configs.image_generation.image_size,
        )

        image_url = result.data[0].url
        self._logger.debug(f"Image generated.")

        # Save the image locally with the current datetime as the filename
        output_dir = os.path.join(os.path.dirname(__file__), f"..{self._configs.image_generation.deliverables_path}")
        os.makedirs(output_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{current_time}.png")

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(output_file, "wb") as f:
                        f.write(await response.read())
                    self._logger.debug(f"Image saved: {current_time}.png")
                else:
                    self._logger.error(f"Failed to download image. Status: {response.status}")
                    raise Exception(f"Failed to download image. Status: {response.status}")

        return image_url, current_time

    async def add_text_overlay(self, image_id: str, text: str, vertical_padding: int) -> None:
        try:
            assets_dir = os.path.join(os.path.dirname(__file__), f"..{self._configs.image_generation.assets_path}")
            deliverables_dir = os.path.join(os.path.dirname(__file__),
                                            f"..{self._configs.image_generation.deliverables_path}")
            font_path = os.path.join(assets_dir, "IMPACTFUL.ttf")
            image_path = os.path.join(deliverables_dir, f"{image_id}.png")

            # Open the image
            with Image.open(image_path) as img:
                draw = ImageDraw.Draw(img)

                # Define font and text properties
                font = ImageFont.truetype(font_path, 90)
                text = text.upper()  # Convert text to uppercase

                # Dynamically calculate the maximum number of characters per line
                max_width = img.width - 20  # Add some padding
                sample_text = "A" * 100  # Sample long text to measure width
                sample_bbox = draw.textbbox((0, 0), sample_text, font=font)
                char_width = (sample_bbox[2] - sample_bbox[0]) / len(sample_text)
                max_chars_per_line = int(max_width / char_width)

                # Wrap text to fit within the image width
                lines = textwrap.wrap(text, width=max_chars_per_line)

                # Calculate starting position for the text
                total_text_height = sum(
                    draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in
                    lines
                )
                start_y = int(img.height * vertical_padding / 100) - total_text_height // 2

                # Add a line_spacing variable to control the spacing between lines
                line_spacing = 20  # Adjust this value as needed

                # Draw each line of text with increased line spacing
                for i, line in enumerate(lines):
                    text_bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_x = (img.width - text_width) // 2
                    text_y = start_y + i * (text_height + line_spacing)  # Add line_spacing here
                    draw.text((text_x, text_y), line, fill="white", font=font, stroke_width=2, stroke_fill="black")

                # Save the modified image
                img.save(image_path)
                self._logger.debug(f"Text overlay added and image saved.")
        except Exception as e:
            self._logger.error(f"Failed to add text overlay: {e}")