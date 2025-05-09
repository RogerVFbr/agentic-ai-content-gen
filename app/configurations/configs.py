from typing import Dict

from pydantic import BaseModel

class Flags(BaseModel):
    agent_log_verbose: bool
    feature_y: bool

class Configs(BaseModel):
    flags: Flags
    remote_credentials: Dict[str, str]