from controllers.worker import MemeGenWorker
from configurations.di_services import AppDi
from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput


def handler(event, context):
    ConfigurationModule().run(
        AppDi.get_service_collection(),
        MemeGenWorker,
        lambda x: x.run(event)
    )

if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    handler(mock_input, None)