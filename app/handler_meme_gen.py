from agents.meme_gen.controllers.worker import MemeGenWorker
from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput


def handler(event, context):
    ConfigurationModule.run(
        MemeGenWorker,
        lambda x: x.run(event)
    )

if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    handler(mock_input, None)