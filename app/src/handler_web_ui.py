from src.configurations.configuration_module import ConfigurationModule
from src.configurations.di_services import AppDi
from src.controllers.web_ui import MemeGenWebUi


module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    web_ui = module.service_provider.get_service(MemeGenWebUi)
else:
    raise Exception("Failed to initialize configuration module.")

if __name__ == "__main__":
    web_ui.run()