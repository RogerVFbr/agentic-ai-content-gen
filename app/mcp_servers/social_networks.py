import sys
from pathlib import Path
import warnings
from fastmcp import FastMCP, Context

warnings.filterwarnings("ignore", category=DeprecationWarning, module="importlib")
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from configurations.configs import Configs  # noqa: E402
from configurations.configuration_module import ConfigurationModule  # noqa: E402
from configurations.di_services import AppDi  # noqa: E402
from repositories.social_networks_repository import SocialNetworksRepository  # noqa: E402

module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    configs: Configs = module.service_provider.get_service(Configs)
    repo: SocialNetworksRepository = module.service_provider.get_service(SocialNetworksRepository)
else:
    raise Exception("Failed to initialize configuration module.")

mcp = FastMCP("social_networks", log_level=configs.mcp.local_servers_log_level)


@mcp.tool()
async def tweet(message: str, ctx: Context) -> dict:
    """Publishes a short message on Twitter (X)."""
    if not configs.flags.enable_publishing:
        return {"success": False, "reason": "Publishing is disabled by configuration. Do not retry."}

    return await repo.tweet(message)


if __name__ == "__main__":
    mcp.run()