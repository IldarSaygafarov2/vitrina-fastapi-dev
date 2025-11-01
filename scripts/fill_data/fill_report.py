import asyncio
import time

from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import fill_row_with_data, client_init_json, get_table_by_url
from tgbot.utils.helpers import correct_advertisement_dict

config = load_config(".env")


async def fill_report(session):
    repo = RequestsRepo(session)

    client = client_init_json()
    buy_table = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    month = 4

    advertisements = await repo.advertisements.get_advertisements_by_month(month, 'RENT')
    advertisements = [
        AdvertisementForReportDTO.model_validate(obj, from_attributes=True).model_dump()
        for obj in advertisements
    ]
    print(len(advertisements))
    for adv in advertisements:
        adv = correct_advertisement_dict(adv)
        fill_row_with_data(buy_table, MONTHS_DICT[month], adv)
        time.sleep(1.5)
        print(f"{adv=}")




async def main() -> None:
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_report(session)


asyncio.run(main())
