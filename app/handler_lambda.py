import asyncio

from controllers.worker import MemeGenWorker
from configurations.di_services import AppDi
from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput


module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    worker = module.service_provider.get_service(MemeGenWorker)
else:
    raise Exception("Failed to initialize configuration module.")

def handler(event, context):
    asyncio.run(worker.run(event))


if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    handler(mock_input, None)