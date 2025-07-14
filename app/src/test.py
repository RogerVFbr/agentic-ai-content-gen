import asyncio

from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from repositories.social_networks_repository import SocialNetworksRepository

module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    repo = module.service_provider.get_service(SocialNetworksRepository)
else:
    raise Exception("Failed to initialize configuration module.")

def handler(event, context):
    asyncio.run(repo.tweet("Hello, world! This is a test tweet!"))


if __name__ == "__main__":
    handler({}, None)