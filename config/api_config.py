from dataclasses import dataclass, field

from environs import Env


@dataclass
class RunConfig:
    api_host: str
    api_port: int

    @staticmethod
    def from_env(env: Env) -> "RunConfig":
        return RunConfig(
            api_host=env.str("API_HOST"),
            api_port=env.int("API_PORT"),
        )


@dataclass
class ApiV1Prefix:
    prefix: str = "/v1"
    districts: str = "/districts"
    categories: str = "/categories"
    advertisements: str = "/advertisements"
    users: str = "/users"
    request: str = "/request"
    consultation: str = "/consultation"
    agents: str = "/agents"
    dev: str = '/dev'


@dataclass
class ApiPrefix:
    prefix: str = "/api"
    v1: ApiV1Prefix = field(default_factory=ApiV1Prefix)
