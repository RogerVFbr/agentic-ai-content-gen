import re

import gradio as gr
import io
import sys
import asyncio
from PIL import Image
from ansi2html import Ansi2HTMLConverter

from controllers.controller import MemeGenController
from configurations.di_services import AppDi
from configurations.configuration_module import ConfigurationModule
from crosscutting.logging.app_logger import AppLogger
from crosscutting.logging.app_logger_config import LogLevel

class LocalUi:

    def __init__(self):
        self.conv = Ansi2HTMLConverter(inline=True, dark_bg=True)
        self.ansi_pattern = r"\u001b\[38;2;(\d+);(\d+);(\d+)m\u001b\[7m(.*?)\u001b\[0m"

    async def log_sample(self) -> None:
        for i in range(5):
            AppLogger.debug(f"Debug message {i}")
            AppLogger.info(f"Info message {i}")
            AppLogger.warn(f"Warning message {i}")
            AppLogger.error(f"Error message {i}")
            AppLogger.critical(f"Critical message {i}")
            AppLogger.highlight_1(f"Highlight 1 message {i}")
            AppLogger.highlight_2(f"Highlight 2 message {i}")
            AppLogger.highlight_3(LogLevel.INFO, f"Highlight 3 message {i}")
            await asyncio.sleep(1)

    def preprocess_ansi_logs(self, ansi_logs):
        def replace_with_span(match):
            r, g, b = match.group(1), match.group(2), match.group(3)
            text = match.group(4)
            return f'<span style="color: #000000; background-color: #{int(r):02X}{int(g):02X}{int(b):02X};">{text}</span>'

        ansi_logs = ansi_logs.replace('[37m', '[38;2;128;128;128m')
        ansi_logs = ansi_logs.replace('[33m', '[38;2;166;138;12m')
        logs = re.sub(self.ansi_pattern, replace_with_span, ansi_logs)
        logs = logs.replace("<timeit>", "-timeit-")
        logs = self.conv.convert(logs, full=True).replace("\n", "<br>")
        logs = logs.replace("&lt;", "<").replace("&gt;", ">")

        return logs

    async def run_memegen(self):
        module = ConfigurationModule()
        services = AppDi.get_service_collection()
        if module.initialize(services):
            controller = module.service_provider.get_service(MemeGenController)
            try:
                await controller.initialize()
                await controller.run({})
            finally:
                await controller.terminate()
        else:
            raise Exception("Failed to initialize configuration module.")

    async def start_process(self):
        stdout_buffer = io.StringIO()
        sys.stdout = stdout_buffer

        try:
            worker_task = asyncio.create_task(self.run_memegen())
            # worker_task = asyncio.create_task(log_stuff())
            while not worker_task.done():
                await asyncio.sleep(1)
                ansi_logs = self.preprocess_ansi_logs(stdout_buffer.getvalue())
                yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), None

            ansi_logs = self.preprocess_ansi_logs(stdout_buffer.getvalue())
            yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), None
        finally:
            sys.stdout = sys.__stdout__

        final_image = Image.new("RGB", (200, 200), color="blue")
        yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), gr.update(value=final_image)

    @staticmethod
    def get_js():
        return """
        function scrollToBottom() {
            console.log("JavaScript script loaded and running.");
            const terminal = document.getElementById('terminal');
            if (terminal) {
                console.log("Terminal element found. Setting up MutationObserver.");
                const observer = new MutationObserver(() => {
                    console.log("Content changed. Scrolling to the bottom.");
                    terminal.scrollTo({ top: terminal.scrollHeight, behavior: "smooth" });
                });
                observer.observe(terminal, { childList: true, subtree: true });
            }
        }
        """

    @staticmethod
    def get_css():
        return """
        #terminal {
            background-color: black;
            padding: 10px;
            border-radius: 5px;
            overflow-y: auto;
            overflow-x: hidden; /* Enable horizontal scrolling */
            height: 800px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
        
        #terminal > div {
            color: white;
            margin-bottom: 5px;
            white-space: pre-wrap; /* Ensure text wraps properly */
            overflow-wrap: anywhere; /* Break long words */
        }
        
        #terminal > div span {
            white-space: pre-wrap; /* Ensure spans also wrap properly */
            overflow-wrap: anywhere; /* Break long words inside spans */
        }
        
        #image_output {
            height: 800px;
        }
        """

    def run(self):
        with gr.Blocks(js=self.get_js(), css=self.get_css()) as demo:
            gr.Markdown("# MemeGen Local Demo")
            start_button = gr.Button("Generate Meme!", variant="primary")
            with gr.Row():
                with gr.Column(scale=65):
                    logs_output = gr.HTML(label="Logs", elem_id="terminal")
                with gr.Column(scale=35):
                    image_output = gr.Image(label="Final Image", elem_id="image_output", interactive=False)

            start_button.click(self.start_process, outputs=[logs_output, image_output])

        demo.launch()