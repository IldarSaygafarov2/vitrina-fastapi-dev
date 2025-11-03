from dataclasses import dataclass
import environs


@dataclass
class ReminderConfig:
    buy_reminder_days: int
    rent_reminder_days: int

    buy_reminder_minutes: int
    rent_reminder_minutes: int

    @staticmethod
    def from_env(env: environs.Env) -> "ReminderConfig":
        return ReminderConfig(
            rent_reminder_days=env.int("RENT_REMINDER_DAYS"),
            buy_reminder_days=env.int("BUY_REMINDER_DAYS"),

            rent_reminder_minutes=env.int("RENT_REMINDER_MINUTES"),
            buy_reminder_minutes=env.int("BUY_REMINDER_MINUTES"),
        )
