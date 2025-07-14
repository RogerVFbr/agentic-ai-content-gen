import asyncio

from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from controllers.worker import MemeGenWorker


module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    worker = module.service_provider.get_service(MemeGenWorker)
else:
    raise Exception("Failed to initialize configuration module.")

def handler(event, context):
    asyncio.run(worker.run(event))


if __name__ == "__main__":
    handler({}, None)