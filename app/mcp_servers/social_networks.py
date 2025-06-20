import json
import sys
from pathlib import Path
import warnings
from fastmcp import FastMCP, Context

warnings.filterwarnings("ignore", category=DeprecationWarning, module="importlib")
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from configurations.configs import Configs
from configurations.configuration_module import ConfigurationModule
from configurations.di_services import AppDi
from repositories.social_networks_repository import SocialNetworksRepository

module = ConfigurationModule()
services = AppDi.get_service_collection()
if module.initialize(services):
    configs: Configs = module.service_provider.get_service(Configs)
    repo: SocialNetworksRepository = module.service_provider.get_service(SocialNetworksRepository)
else:
    raise Exception("Failed to initialize configuration module.")

mcp = FastMCP("social_networks", log_level=configs.mcp.local_servers_log_level)


@mcp.tool()
async def tweet(message: str, ctx: Context) -> str:
    """Publishes a short message on Twitter (X)."""
    if not configs.flags.enable_publishing:
        await ctx.warning("Publishing is disabled by configuration.")
        return json.dumps({"success": False, "reason": "Publishing is disabled by configuration. Do not retry."})

    await repo.tweet(message)
    return json.dumps({"success": True, "reason": "N.A."})


if __name__ == "__main__":
    mcp.run()