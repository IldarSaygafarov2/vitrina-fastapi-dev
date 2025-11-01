from backend.app.config import config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.googlesheets.main import GoogleSheet

engine = create_engine(config.db, echo=True)
session_pool = create_session_pool(engine)


async def get_repo():
    async with session_pool() as session:
        yield RequestsRepo(session)


def get_google_sheet():
    return GoogleSheet(spreadsheet_id=config.google_sheet.spreadsheet_id)
