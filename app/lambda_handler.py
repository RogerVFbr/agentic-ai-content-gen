from configurations.configuration_module import ConfigurationModule
from controllers.app_controller import AppController


def handler(event, context):
    config = ConfigurationModule.get()
    if config.initialize():
        controller = config.get_instance(AppController)
        controller.run(event)
