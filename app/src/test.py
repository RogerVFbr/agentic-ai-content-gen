import asyncio

from src.configurations import AppDi
from src.configurations import ConfigurationModule
from src.repositories import SocialNetworksRepository
from tests.mock_input import MockInput


module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    repo = module.service_provider.get_service(SocialNetworksRepository)
else:
    raise Exception("Failed to initialize configuration module.")

def handler(event, context):
    asyncio.run(repo.tweet("Hello, world! This is a test tweet!"))


if __name__ == "__main__":
    mock_input = MockInput.get_basic_research()
    handler(mock_input, None)