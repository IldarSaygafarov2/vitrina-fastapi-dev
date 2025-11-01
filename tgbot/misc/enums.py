from enum import Enum
from backend.app.config import config

class RentForumTopicEnum(Enum):
    TOPIC_300_600 = (24, [300, 600])
    TOPIC_600_900 = (28, [600, 900])
    TOPIC_1000_1500 = (2, [1000, 1500])
    TOPIC_1500_GT = (7, [1500, 10_000])


# RENT_FORUM_TOPIC_DATA = {
#     24: [300, 600],
#     28: [600, 900],
#     2: [1000, 1500],
#     7: [1500, 10_000]
# }




class BuyForumTopicEnum(Enum):
    TOPIC_30K_60K = (11, [30_0000, 60_000])  # стоимость от 30.000 до 60.000
    TOPIC_60K_80K = (10, [60_000, 80_000])  # стоимость от 60.000 до 80.000
    TOPIC_80K_120K = (9, [80_000, 120_000])  #  стоимость от 80.000 до 120.000
    TOPIC_150K_GT = (7, [150_000, 1_000_000])  # стоимость выше 150.000

