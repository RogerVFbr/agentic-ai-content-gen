from configurations.configuration_module import ConfigurationModule
from workers.crewai_worker import CrewAiWorker
from workers.langgraph_worker import LangGraphWorker


def handler_langgraph(event, context):
    ConfigurationModule.run(
        LangGraphWorker,
        lambda x: x.run(event)
    )

def handler_crewai(event, context):
    ConfigurationModule.run(
        CrewAiWorker,
        lambda x: x.run(event)
    )
