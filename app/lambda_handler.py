from configurations.configuration_module import ConfigurationModule
from controllers.app_controller import AppController


def handler(event, context):
    if ConfigurationModule.initialize():
        controller = ConfigurationModule.get_instance(AppController)
        controller.run()
