from dataclasses import dataclass

from environs import Env
import json


@dataclass
class TgBot:
    token: str
    rent_channel_name: str
    buy_channel_name: str
    base_channel_name: str
    main_chat_id: int
    test_main_chat_id: int
    supergroup_id: int

    @staticmethod
    def from_env(env: Env) -> "TgBot":
        return TgBot(
            token=env.str("BOT_API_TOKEN"),
            rent_channel_name=env.str("RENT_CHANNEL"),
            buy_channel_name=env.str("BUY_CHANNEL"),
            base_channel_name=env.str("BASE_CHANNEL"),
            main_chat_id=env.int("MAIN_CHAT_ID"),
            test_main_chat_id=env.int("TEST_MAIN_CHAT_ID"),
            supergroup_id=env.int("SUPERGROUP_ID")
        )


@dataclass
class TgSuperGroupConfig:
    rent_supergroup_id: str
    buy_supergroup_id: str

    rent_topic_thread_ids: str
    rent_topic_prices: str

    buy_topic_thread_ids: str
    buy_topic_prices: str

    @staticmethod
    def from_env(env: Env) -> "TgSuperGroupConfig":
        return TgSuperGroupConfig(
            rent_supergroup_id=env.str('RENT_SUPERGROUP_ID'),
            buy_supergroup_id=env.str('BUY_SUPERGROUP_ID'),

            rent_topic_thread_ids=env.str('RENT_TOPIC_THREAD_IDS'),
            rent_topic_prices=env.str('RENT_TOPIC_PRICES'),

            buy_topic_thread_ids=env.str('BUY_TOPIC_THREAD_IDS'),
            buy_topic_prices=env.str('BUY_TOPIC_PRICES'),
        )

    def get_topic_thread_ids(self, topic_type: str):
        if topic_type == 'Аренда':
            return list(map(int, self.rent_topic_thread_ids.split('/')))
        elif topic_type == 'Покупка':
            return list(map(int, self.buy_topic_thread_ids.split('/')))
        else:
            raise ValueError(f'Invalid topic type: {topic_type}')

    def get_topic_prices(self, topic_type: str):
        prices = []
        if topic_type == 'Аренда':
            prices = self.rent_topic_prices.split('/')
        elif topic_type == 'Покупка':
            prices = self.buy_topic_prices.split('/')
        return [list(map(int, s.strip('[]').replace('_', '').split(', '))) for s in prices]

    def make_forum_topics_data(self, topic_type: str):
        thread_ids = self.get_topic_thread_ids(topic_type)

        prices = self.get_topic_prices(topic_type)
        return dict(zip(thread_ids, prices))


