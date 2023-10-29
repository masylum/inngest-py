import enum

import pydantic

from . import function_config, types


class DeployType(enum.Enum):
    PING = "ping"


class RegisterRequest(types.BaseModel):
    app_name: str
    deploy_type: DeployType
    framework: str
    functions: list[function_config.FunctionConfig] = pydantic.Field(
        min_length=1
    )
    sdk: str
    url: str
    v: str
