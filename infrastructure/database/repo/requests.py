from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .advertisement import AdvertisementRepo, AdvertisementImageRepo, AdvertisementQueueRepo
from .category import CategoryRepo
from .consultation import ConsultationRepo
from .district import DistrictRepo
from .user import UserRepo
from .user_request import UserRequestRepo


@dataclass
class RequestsRepo:
    session: AsyncSession

    @property
    def categories(self) -> CategoryRepo:
        return CategoryRepo(self.session)

    @property
    def districts(self) -> DistrictRepo:
        return DistrictRepo(self.session)

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def advertisements(self) -> AdvertisementRepo:
        return AdvertisementRepo(self.session)

    @property
    def advertisement_images(self) -> AdvertisementImageRepo:
        return AdvertisementImageRepo(self.session)

    @property
    def advertisement_queue(self) -> AdvertisementQueueRepo:
        return AdvertisementQueueRepo(self.session)

    @property
    def user_request(self) -> UserRequestRepo:
        return UserRequestRepo(self.session)

    @property
    def consultation(self) -> ConsultationRepo:
        return ConsultationRepo(self.session)
