from dataclasses import dataclass
import environs


@dataclass
class ReminderConfig:
    buy_reminder_days: int
    rent_reminder_days: int

    @staticmethod
    def from_env(env: environs.Env) -> "ReminderConfig":
        return ReminderConfig(
            rent_reminder_days=env.int("RENT_REMINDER_DAYS"),
            buy_reminder_days=env.int("BUY_REMINDER_DAYS")
        )
