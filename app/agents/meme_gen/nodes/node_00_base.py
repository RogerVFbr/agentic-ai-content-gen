import re
import yaml
from datetime import datetime
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI

from crosscutting.logging.app_logger import AppLogger
from crosscutting.logging.app_logger_config import LogLevel


class MemeGenBase:

    PROMPT_CACHE = {}

    def __init__(self, logger: AppLogger):
        self.logger = logger

    def load_prompts(self, file_path: str) -> dict:
        if file_path not in self.PROMPT_CACHE:
            with open(file_path, 'r') as file:
                self.PROMPT_CACHE[file_path] = yaml.safe_load(file)
        return self.PROMPT_CACHE[file_path]

    @staticmethod
    def time_now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_llm(temperature: float = 0.0):
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature
        )

    async def log_progress(self, step):
        index = -1
        latest_message = step['messages'][index]
        if isinstance(latest_message, AIMessage):
            if latest_message.tool_calls:
                for tool_call in latest_message.tool_calls:
                    tool_name = tool_call.get("name", "Unknown Tool")
                    tool_status = tool_call.get("args", {})
                    await self.thoughts(LogLevel.DEBUG, f"[{tool_name}] Tool call requested. Args: {tool_status}")
            else:
                content = re.sub(r'\s+', ' ', latest_message.content)
                content = content.replace("\n", " ")
                content = content.replace("```json", " ")
                content = content.replace("#", "")
                content = content.replace("*", "")
                content = content[:150]
                await self.thoughts(LogLevel.DEBUG, f"[AI] {content}" + (" (...)" if len(content) > 150 else ""))
        if isinstance(latest_message, ToolMessage):
            tool_message = step['messages'][index]
            while isinstance(tool_message, ToolMessage):
                tool_name = tool_message.name
                tool_status = tool_message.status
                await self.thoughts(LogLevel.DEBUG, f"[{tool_name}] Tool call status: {tool_status.upper()}")
                index -= 1
                tool_message = step['messages'][index]

    async def thoughts(self, level: LogLevel, msg: str):
        """
        Logging tool for super short sentences..

        Args:
            level (LogLevel): The logging level, which determines the severity of the log. Possible values include:
                - LogLevel.DEBUG: For detailed diagnostic information, useful during development or debugging.
                - LogLevel.INFO: For general informational messages that highlight the progress of the application.
                - LogLevel.WARN: For potentially harmful situations that do not interrupt the application flow.
                - LogLevel.ERROR: For error events that might still allow the application to continue running.
                - LogLevel.CRITICAL: For severe error events that will likely lead to application termination.
            msg (str): The message to be logged, typically representing the agent's thought, action, or status.

        Best Practices:
            - Use DEBUG for verbose output during development or troubleshooting.
            - Use INFO for high-level application flow or significant events.
            - Use WARN for unexpected situations that are not errors but may require attention.
            - Use ERROR for issues that affect functionality but do not stop the application.
            - Use CRITICAL for unrecoverable errors or situations requiring immediate attention.

        This method formats and logs the message using the provided logger instance.
        """
        if level == LogLevel.DEBUG:
            self.logger.highlight_3(f"{msg}")
        elif level == LogLevel.INFO:
            self.logger.highlight_3(f"{msg}")
        elif level == LogLevel.WARN:
            self.logger.warn(f"{msg}")
        elif level == LogLevel.ERROR:
            self.logger.warn(f"{msg}")
        else:
            self.logger.warn(f"{msg}")

    def get_user_message(self, input: str):
        return {
            "messages": [
                {
                    "role": "user",
                    "content": input
                }
            ]
        }