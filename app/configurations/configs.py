from typing import Dict

from pydantic import BaseModel

class Flags(BaseModel):
    EnableFeatureX: bool
    EnableFeatureY: bool

class Configs(BaseModel):
    Flags: Flags
    RemoteCredentials: Dict[str, str]