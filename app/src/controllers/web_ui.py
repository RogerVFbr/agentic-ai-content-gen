import re

import gradio as gr
import io
import sys
import asyncio
from PIL import Image
from ansi2html import Ansi2HTMLConverter

from controllers.controller import MemeGenController

class MemeGenWebUi:

    def __init__(self,
                 controller: MemeGenController):

        self._controller = controller
        self._conv = Ansi2HTMLConverter(inline=True, dark_bg=True)
        self._ansi_pattern = r"\u001b\[38;2;(\d+);(\d+);(\d+)m\u001b\[7m(.*?)\u001b\[0m"

    def run(self):
        with gr.Blocks(js=self._get_js(), css=self._get_css()) as demo:
            gr.Markdown("# MemeGen Local Demo")
            start_button = gr.Button("Generate Meme!", variant="primary")
            with gr.Row():
                with gr.Column(scale=65):
                    logs_output = gr.HTML(label="Logs", elem_id="terminal")
                with gr.Column(scale=35):
                    image_output = gr.Image(label="Final Image", elem_id="image_output", interactive=False)

            start_button.click(self._start_process, outputs=[logs_output, image_output])

        demo.launch()

    async def _run_controller(self):
        try:
            await self._controller.initialize()
            await self._controller.run({})
        finally:
            await self._controller.terminate()

    async def _start_process(self):
        stdout_buffer = io.StringIO()
        sys.stdout = stdout_buffer

        try:
            worker_task = asyncio.create_task(self._run_controller())

            while not worker_task.done():
                await asyncio.sleep(1)
                ansi_logs = self._preprocess_ansi_logs(stdout_buffer.getvalue())
                yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), None

            ansi_logs = self._preprocess_ansi_logs(stdout_buffer.getvalue())
            yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), None
        finally:
            sys.stdout = sys.__stdout__

        final_image = Image.new("RGB", (200, 200), color="blue")
        yield gr.update(value=f"<div style='font-family: monospace; font-size: 12px;'>{ansi_logs}</div>"), gr.update(value=final_image)

    def _preprocess_ansi_logs(self, ansi_logs):
        def replace_with_span(match):
            r, g, b = match.group(1), match.group(2), match.group(3)
            text = match.group(4)
            return f'<span style="color: #000000; background-color: #{int(r):02X}{int(g):02X}{int(b):02X};">{text}</span>'

        ansi_logs = ansi_logs.replace('[37m', '[38;2;128;128;128m')
        ansi_logs = ansi_logs.replace('[33m', '[38;2;166;138;12m')
        logs = re.sub(self._ansi_pattern, replace_with_span, ansi_logs)
        logs = logs.replace("<timeit>", "-timeit-")
        logs = self._conv.convert(logs, full=True).replace("\n", "<br>")
        logs = logs.replace("&lt;", "<").replace("&gt;", ">")

        return logs

    @staticmethod
    def _get_js():
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
    def _get_css():
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