from dataclasses import dataclass
import environs


@dataclass
class RedisConfig:
    broker_url: str
    backend_url: str

    @staticmethod
    def from_env(env: environs.Env) -> "RedisConfig":
        return RedisConfig(
            broker_url=env.str("REDIS_BROKER_URL"),
            backend_url=env.str("REDIS_BACKEND_URL"),
        )