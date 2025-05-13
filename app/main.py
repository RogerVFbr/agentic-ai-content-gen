from crosscutting.logging.app_logger import AppLogger
from lambda_handlers import handler_langgraph
from tests.mock_input import MockInput

if __name__ == "__main__":
    AppLogger.STRUCTURED = False

    mockinput = MockInput.get_langgraph()
    handler_langgraph(mockinput, None)

    # mockinput = MockInput.get_crewai()
    # handler_crewai(mockinput, None)
