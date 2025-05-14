from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput
from agents.content_gen.controllers.worker import ContentGenWorker


def handler(event, context):
    ConfigurationModule.run(
        ContentGenWorker,
        lambda x: x.run(event)
    )


if __name__ == "__main__":
    mock_input = MockInput.get_content_gen()
    handler(mock_input, None)
