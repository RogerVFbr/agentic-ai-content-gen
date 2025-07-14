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

    def load_prompts(self, file_path: str, node: str) -> dict:
        if file_path not in self.PROMPT_CACHE:
            with open(file_path, 'r') as file:
                self.PROMPT_CACHE[file_path] = yaml.safe_load(file)
        return self.PROMPT_CACHE[file_path][node]

    @staticmethod
    def time_now():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_llm(temperature: float = 0.0):
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature
        )

    @staticmethod
    def get_structured_response(response):
        return response["structured_response"] if "structured_response" in response else response["generate_structured_response"]["structured_response"]

    async def log_progress(self, step):
        if 'structured_response' in step:
            self.logger.highlight_3(LogLevel.DEBUG, f"Structured response generated ({type(step['structured_response'])}).")
            return
        if 'generate_structured_response' in step:
            self.logger.highlight_3(LogLevel.DEBUG, f"Structured response generated ({type(step['generate_structured_response']['structured_response'])}).")
            return
        index = -1
        if 'agent' in step:
            latest_message = step['agent']['messages'][index]
        elif 'tools' in step:
            latest_message = step['tools']['messages'][index]
        else:
            latest_message = step['messages'][index]
        if isinstance(latest_message, AIMessage):
            if latest_message.tool_calls:
                for tool_call in latest_message.tool_calls:
                    tool_name = tool_call.get("name", "Unknown Tool")
                    tool_status = tool_call.get("args", {})
                    self.logger.highlight_3(LogLevel.DEBUG, f"[{tool_name}] Tool call requested. Args: {tool_status}")
            else:
                content = latest_message.content.replace("\n", " ")
                content = content.replace("```json", " ")
                content = content.replace("#", "")
                content = content.replace("*", "")
                content = re.sub(r'\s+', ' ', content)
                content = content[:150]
                self.logger.highlight_3(LogLevel.DEBUG, f"[AI] {content}" + (" (...)" if len(latest_message.content) > 150 else ""))
        if isinstance(latest_message, ToolMessage):
            tool_message = latest_message
            while isinstance(tool_message, ToolMessage):
                tool_name = tool_message.name
                tool_status = tool_message.status
                self.logger.highlight_3(LogLevel.DEBUG, f"[{tool_name}] Tool call status: {tool_status.upper()}")
                index -= 1
                if 'agent' in step:
                    if len(step['agent']['messages']) < abs(index):
                        break
                    tool_message = step['agent']['messages'][index]
                elif 'tools' in step:
                    if len(step['tools']['messages']) < abs(index):
                        break
                    tool_message = step['tools']['messages'][index]
                else:
                    if len(step['messages']) < abs(index):
                        break
                    tool_message = step['messages'][index]

    def get_user_message(self, input: str):
        return {
            "messages": [
                {
                    "role": "user",
                    "content": input
                }
            ]
        }