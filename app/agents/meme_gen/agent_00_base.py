from crosscutting.logging.app_logger import AppLogger
from crosscutting.logging.app_logger_config import LogLevel


class MemeGenBase:

    def __init__(self, logger: AppLogger):
        self.logger = logger

    async def thoughts(self, level: LogLevel, msg: str):
        """
        Logs messages generated during the agent's execution.

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
            self.logger.debug(f"[LLM] {msg}")
        elif level == LogLevel.INFO:
            self.logger.info(f"[LLM] {msg}")
        elif level == LogLevel.WARN:
            self.logger.warn(f"[LLM] {msg}")
        elif level == LogLevel.ERROR:
            self.logger.error(f"[LLM] {msg}")
        else:
            self.logger.critical(f"[LLM] {msg}")

    def get_user_message(self, input: str):
        return {
            "messages": [
                {
                    "role": "user",
                    "content": input
                }
            ]
        }