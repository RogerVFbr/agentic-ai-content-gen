from crosscutting.app_logger import AppLogger
from lambda_handler import handler
from tests.mock_input import MockInput

if __name__ == "__main__":
    AppLogger.STRUCTURED = False
    mockinput = MockInput.get()
    handler(mockinput, None)
