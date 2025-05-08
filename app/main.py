from crosscutting.app_logger import AppLogger
from lambda_handler import handler

if __name__ == "__main__":
    AppLogger.STRUCTURED = False
    handler(None, None)
