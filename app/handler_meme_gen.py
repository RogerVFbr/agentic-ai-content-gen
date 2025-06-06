import asyncio

from controllers.worker import MemeGenWorker
from configurations.di_services import AppDi
from configurations.configuration_module import ConfigurationModule
from tests.mock_input import MockInput


worker = None
module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    worker = module.service_provider.get_service(MemeGenWorker)
else:
    raise Exception("Failed to initialize configuration module.")

async def handler(event, context):
    await worker.run(event)


if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    asyncio.run(handler(mock_input, None))