import asyncio

from configurations.configuration_module import ConfigurationModule
from workers.crewai_worker import CrewAiWorker
from workers.langgraph_worker import LangGraphWorker


def handler_langgraph(event, context):
    async def execute():
        config = ConfigurationModule.get()
        if config.initialize():
            worker = config.get_instance(LangGraphWorker)
            await worker.run(event)

    asyncio.run(execute())


def handler_crewai(event, context):
    async def execute():
        config = ConfigurationModule.get()
        if config.initialize():
            worker = config.get_instance(CrewAiWorker)
            await worker.run(event)

    asyncio.run(execute())
