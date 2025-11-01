from dataclasses import dataclass

from environs import Env
from sqlalchemy.engine.url import URL


@dataclass
class DbConfig:
    host: str
    user: str
    password: str
    database: str
    port: int = 5432

    def construct_sqlalchemy_url(self, driver='asyncpg') -> str:
        return URL.create(
            drivername=f'postgresql+{driver}',
            username=self.user,
            password=self.password,
            host=self.host,
            database=self.database,
            port=self.port,
        ).render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env) -> "DbConfig":
        return DbConfig(
            host=env.str('DB_HOST'),
            user=env.str('DB_USER'),
            password=env.str('DB_PASSWORD'),
            database=env.str('DB_NAME'),
            port=env.int('DB_PORT'),
        )
