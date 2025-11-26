import shutil
from pathlib import Path
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.user.inline import (
    advertisement_choices_kb,
    advertisement_images_kb,
    advertisement_update_kb,
    categories_kb,
    districts_kb,
    return_back_kb,
)
from tgbot.misc.user_states import AdvertisementUpdateState
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.advertisement_updating import (
    update_address_text,
    update_category_text,
    update_creation_date_text,
    update_description_text,
    update_district_text,
    update_floor_text,
    update_house_quadrature_text,
    update_name_text,
    update_operation_type_text,
    update_owner_phone_number_text,
    update_price_text,
    update_property_type_text,
    update_quadrature_text,
    update_repair_type_text,
    update_rooms_text,
)

from tgbot.utils.helpers import get_media_group, download_file

router = Router()


@router.callback_query(F.data.startswith("advertisement_update"))
async def process_advertisement_update(
    call: types.CallbackQuery,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])

    await call.message.edit_text(
        text="Выберите поле, которое хотите изменить",
        reply_markup=advertisement_update_kb(advertisement_id=advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_name"))
async def update_advertisement_name(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await state.set_state(AdvertisementUpdateState.name)

    await call.message.edit_text(
        text=update_name_text(current=advertisement.name),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.message(AdvertisementUpdateState.name)
async def get_new_name(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=data["advertisement_id"],
        name=message.text,
    )
    await message.answer(
        realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id=data["advertisement_id"]),
    )


@router.callback_query(F.data.startswith("uz_update_advertisement_name"))
async def update_advertisement_name_uz(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await state.set_state(AdvertisementUpdateState.name_uz)

    await call.message.edit_text(
        text=update_name_text(current=advertisement.name_uz),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.message(AdvertisementUpdateState.name_uz)
async def get_new_name_uz(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=data["advertisement_id"],
        name_uz=message.text,
    )
    await message.answer(
        realtor_advertisement_completed_text(updated, lang="uz"),
        reply_markup=advertisement_update_kb(advertisement_id=data["advertisement_id"]),
    )


@router.callback_query(F.data.startswith("update_advertisement_owner_phone_number"))
async def update_advertisement_owner_phone_number(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.answer(
        text=update_owner_phone_number_text(current=advertisement.owner_phone_number),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.owner_phone_number)


@router.message(AdvertisementUpdateState.owner_phone_number)
async def update_advertisement_owner_phone_number(
    message: types.Message, repo: "RequestsRepo", state: FSMContext
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")
    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        owner_phone_number=message.text,
    )
    await message.answer(
        realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id=data["advertisement_id"]),
    )


@router.callback_query(F.data.startswith("update_advertisement_operation_type"))
async def update_operation_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_operation_type_text(current=advertisement.operation_type.value),
        reply_markup=advertisement_choices_kb(choice_type="operation_type"),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_operation_type"))
async def get_new_operation_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    await call.answer()

    _, operation_type = call.data.split(":")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=data["advertisement_id"],
        operation_type=operation_type.upper(),
    )
    await call.message.edit_text(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id=data["advertisement_id"]),
    )


@router.callback_query(F.data.startswith("update_advertisement_gallery"))
async def update_gallery(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    images = advertisement.images
    photos = [obj.tg_image_hash for obj in images if obj.tg_image_hash]
    if not photos:
        photos = [obj.url for obj in images]

    media_group = get_media_group(photos)

    await call.message.answer_media_group(media=media_group)
    await call.message.answer(
        text="Выберите фотографию которую хотите обновить",
        reply_markup=advertisement_images_kb(images),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_advertisement_description"))
async def update_description(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_description_text(current=advertisement.description),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )

    await state.set_state(AdvertisementUpdateState.description)
    await state.update_data(advertisement_id=advertisement_id)


@router.message(AdvertisementUpdateState.description)
async def get_new_description(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        description=message.text,
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("uz_update_advertisement_description"))
async def update_description(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_description_text(current=advertisement.description_uz),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )

    await state.set_state(AdvertisementUpdateState.description_uz)
    await state.update_data(advertisement_id=advertisement_id)


@router.message(AdvertisementUpdateState.description_uz)
async def get_new_description(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        description_uz=message.text,
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated, lang="uz"),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_district"))
async def update_district(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    districts = await repo.districts.get_districts()

    await call.message.edit_text(
        text=update_district_text(current=advertisement.district.name),
        reply_markup=districts_kb(districts=districts, for_update=True),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_chosen_district"))
async def get_new_district(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    district_id = int(call.data.split(":")[-1])

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        district_id=district_id,
    )
    await call.message.edit_text(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_address"))
async def update_address(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_address_text(current=advertisement.address),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.address)


@router.message(AdvertisementUpdateState.address)
async def get_new_address(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        address=message.text,
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("uz_update_advertisement_address"))
async def update_address(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_address_text(current=advertisement.address_uz),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.address_uz)


@router.message(AdvertisementUpdateState.address_uz)
async def get_new_address(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        address_uz=message.text,
    )

    await message.answer(
        text=realtor_advertisement_completed_text(updated, lang="uz"),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_property_category"))
async def update_advertisement_category(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    categories = await repo.categories.get_categories()

    await call.message.edit_text(
        text=update_category_text(current=advertisement.category.name),
        reply_markup=categories_kb(categories=categories, for_update=True),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_chosen_category"))
async def get_new_category(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    category_id = int(call.data.split(":")[-1])

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        category_id=category_id,
    )

    await call.message.edit_text(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_property_type"))
async def update_property_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    await call.message.edit_text(
        text=update_property_type_text(current=advertisement.property_type.value),
        reply_markup=advertisement_choices_kb(choice_type="property_type"),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_property_type"))
async def get_new_property_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    _, property_type = call.data.split(":")
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        property_type=property_type.upper(),
    )
    await call.message.edit_text(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_price"))
async def update_advertisement_price(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_price_text(current=advertisement.price),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.set_state(AdvertisementUpdateState.price)
    await state.update_data(advertisement_id=advertisement_id)


@router.message(AdvertisementUpdateState.price)
async def get_new_price(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        price=int(message.text),
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id=advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_quadrature"))
async def update_quadrature(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    await call.message.edit_text(
        text=update_quadrature_text(
            current=f"{advertisement.quadrature_from}, {advertisement.quadrature_to}"
        ),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.quadrature)


@router.message(AdvertisementUpdateState.quadrature)
async def get_new_quadrature(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        quadrature=int(message.text),
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_creation_date"))
async def update_creation_date(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_creation_date_text(current=advertisement.creation_year),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.creation_year)


@router.message(AdvertisementUpdateState.creation_year)
async def get_new_creation_year(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        creation_year=int(message.text),
    )

    await message.answer(
        realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_rooms"))
async def update_rooms(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    await call.message.edit_text(
        text=update_rooms_text(current=f"{advertisement.rooms_quantity}"),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.rooms)


@router.message(AdvertisementUpdateState.rooms)
async def get_new_rooms_qty(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id, rooms_quantity=int(message.text)
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_repair_type"))
async def update_repair_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.edit_text(
        text=update_repair_type_text(current=advertisement.repair_type.value),
        reply_markup=advertisement_choices_kb(choice_type="repair_type"),
    )
    await state.update_data(advertisement_id=advertisement_id)


@router.callback_query(F.data.startswith("update_repair_type"))
async def get_new_repair_type(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")
    _, repair_type = call.data.split(":")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        repair_type=repair_type.upper(),
    )
    await call.message.edit_text(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_house_quadrature"))
async def update_house_quadrature(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    current = (
        f"{advertisement.house_quadrature_from}, {advertisement.house_quadrature_to}"
    )

    await call.message.edit_text(
        text=update_house_quadrature_text(current=current),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.house_quadrature)


@router.message(AdvertisementUpdateState.house_quadrature)
async def get_new_house_quadrature(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    _from, to = message.text.split(", ")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        house_quadrature_from=int(_from),
        house_quadrature_to=int(to),
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("update_advertisement_floor"))
async def update_advertisement_floor(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    current = f"{advertisement.floor_from}, {advertisement.floor_to}"

    await call.message.edit_text(
        text=update_floor_text(current=current),
        reply_markup=return_back_kb(f"advertisement_update:{advertisement_id}"),
    )
    await state.update_data(advertisement_id=advertisement_id)
    await state.set_state(AdvertisementUpdateState.floor)


@router.message(AdvertisementUpdateState.floor)
async def get_new_floor(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()
    advertisement_id = data.get("advertisement_id")

    _from, to = message.text.split(", ")

    updated = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        floor_from=int(_from),
        floor_to=int(to),
    )
    await message.answer(
        text=realtor_advertisement_completed_text(updated),
        reply_markup=advertisement_update_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("adv_img"))
async def update_image(
    call: types.CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    image_id = int(call.data.split(":")[-1])

    image_obj = await repo.advertisement_images.get_image_by_id(image_id=image_id)

    media_image_obj = types.InputMediaPhoto(media=image_obj.tg_image_hash)

    await call.message.answer_media_group(media=[media_image_obj])
    await call.message.answer(
        text="отправьте новую фотографию",
        reply_markup=None,
    )
    await state.update_data(image_id=image_id)
    await state.set_state(AdvertisementUpdateState.image)


@router.message(AdvertisementUpdateState.image)
async def get_new_image(
    message: types.Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    image_id = state_data.get("image_id")
    advertisement_id = state_data.get("advertisement_id")

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    image = await repo.advertisement_images.get_image_by_id(image_id=image_id)

    # adding new image
    new_image_id = message.photo[-1].file_id
    current_image_dir = "/".join(image.url.split("/")[:-1])

    file, filename = await download_file(bot=message.bot, file_id=new_image_id)

    file_location = Path(current_image_dir) / filename

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file, f)

    # updating existing image
    await repo.advertisement_images.update_image(
        image_id=image_id,
        url=str(file_location),
        tg_image_hash=new_image_id,
    )

    # advertisement message
    advertisement_message = realtor_advertisement_completed_text(advertisement)
    images = advertisement.images
    photos = [obj.tg_image_hash for obj in images if obj.tg_image_hash]
    if not photos:
        photos = [obj.url for obj in images]

    media_group = get_media_group(photos, advertisement_message)

    await message.answer_media_group(media=media_group)
    await message.answer(
        text="Фотография была обновлена\nВыберите поле, которое хотите изменить",
        reply_markup=advertisement_update_kb(advertisement_id=advertisement_id),
    )
