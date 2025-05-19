from agents.basic_research.controllers.worker import BasicResearchWorker
from agents.basic_research.di import BasicResearchDi
from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput


def handler(event, context):
    ConfigurationModule.run(
        BasicResearchDi.get_pre_instantiated(),
        BasicResearchDi.get_service_collection(),
        BasicResearchWorker,
        lambda x: x.run(event)
    )

if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    handler(mock_input, None)