from dataclasses import dataclass
from typing import Optional

from environs import Env

from .api_config import ApiPrefix, RunConfig
from .db_config import DbConfig
from .google_sheet_config import GoogleSheetConfig, ReportSheetConfig
from .tg_config import TgBot, TgSuperGroupConfig
from .reminder_config import ReminderConfig


@dataclass
class Config:
    db: DbConfig
    api_prefix: ApiPrefix
    run_api: RunConfig
    tg_bot: TgBot
    google_sheet: GoogleSheetConfig
    super_group: TgSuperGroupConfig
    report_sheet: ReportSheetConfig
    reminder_config: ReminderConfig


def load_config(path: Optional[str] = None) -> "Config":
    env = Env()
    env.read_env(path)

    db_config = DbConfig.from_env(env)
    run_api_config = RunConfig.from_env(env)
    tg_bot = TgBot.from_env(env)
    google_sheet = GoogleSheetConfig.from_env(env)
    super_group_config = TgSuperGroupConfig.from_env(env)
    report_sheet = ReportSheetConfig.from_env(env)
    reminder_config = ReminderConfig.from_env(env)

    api_prefix = ApiPrefix()

    return Config(
        db=db_config,
        api_prefix=api_prefix,
        run_api=run_api_config,
        tg_bot=tg_bot,
        google_sheet=google_sheet,
        super_group=super_group_config,
        report_sheet=report_sheet,
        reminder_config=reminder_config
    )
