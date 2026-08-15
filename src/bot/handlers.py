from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command

from src.database.session import AsyncSessionLocal
from src.database.repository import UserRepository, SavedSearchRepository, SystemConfigRepository
from src.bot.lexicon import LEXICON, get_text
from src.scraper.service import CopartMockScraper, SearchFilter
from src.calculator.customs import CustomsCalculator
from src.config import settings

router = Router()


class SearchStates(StatesGroup):
    waiting_for_make = State()
    waiting_for_model = State()
    waiting_for_budget = State()
    waiting_for_year = State()
    waiting_for_title = State()


class CalcStates(StatesGroup):
    waiting_for_price = State()
    waiting_for_year = State()
    waiting_for_cc = State()
    waiting_for_fuel = State()


class AdminStates(StatesGroup):
    waiting_for_logistics = State()
    waiting_for_broker_fee = State()


def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=get_text(lang, "btn_search")), KeyboardButton(text=get_text(lang, "btn_calc"))],
        [KeyboardButton(text=get_text(lang, "btn_alerts")), KeyboardButton(text=get_text(lang, "btn_lang"))],
        [KeyboardButton(text=get_text(lang, "btn_broker_panel"))]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_or_create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        lang = user.language_code

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="set_lang:hy"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")
        ]
    ])

    await message.answer(get_text(lang, "welcome"), reply_markup=get_main_keyboard(lang))
    await message.answer(get_text(lang, "choose_lang"), reply_markup=inline_kb)


@router.callback_query(F.data.startswith("set_lang:"))
async def cb_set_lang(callback: CallbackQuery):
    lang_code = callback.data.split(":")[1]
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        await repo.update_language(callback.from_user.id, lang_code)

    await callback.answer()
    await callback.message.edit_text(get_text(lang_code, "lang_set"))
    await callback.message.answer(get_text(lang_code, "main_menu"), reply_markup=get_main_keyboard(lang_code))


@router.message(F.text.in_([LEXICON["hy"]["btn_lang"], LEXICON["en"]["btn_lang"]]))
async def msg_change_lang(message: Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="set_lang:hy"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")
        ]
    ])
    await message.answer(get_text("hy", "choose_lang"), reply_markup=inline_kb)


# --- CAR SEARCH HANDLERS ---

@router.message(F.text.in_([LEXICON["hy"]["btn_search"], LEXICON["en"]["btn_search"]]))
async def start_search(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_or_create(message.from_user.id)
        lang = user.language_code

    await state.update_data(lang=lang)
    await state.set_state(SearchStates.waiting_for_make)
    await message.answer(get_text(lang, "search_prompt_make"))


@router.message(SearchStates.waiting_for_make)
async def process_make(message: Message, state: FSMContext):
    make = message.text.strip()
    await state.update_data(make=make)
    data = await state.get_data()
    lang = data.get("lang", "hy")
    await state.set_state(SearchStates.waiting_for_model)
    await message.answer(get_text(lang, "search_prompt_model"))


@router.message(SearchStates.waiting_for_model)
async def process_model(message: Message, state: FSMContext):
    model = None if message.text == "/skip" else message.text.strip()
    await state.update_data(model=model)
    data = await state.get_data()
    lang = data.get("lang", "hy")
    await state.set_state(SearchStates.waiting_for_budget)
    await message.answer(get_text(lang, "search_prompt_budget"))


@router.message(SearchStates.waiting_for_budget)
async def process_budget(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    try:
        budget = float(message.text.replace("$", "").strip())
        await state.update_data(max_budget=budget)
    except ValueError:
        await message.answer("⚠️ Invalid number. Please enter budget as e.g. 7000:")
        return

    await state.set_state(SearchStates.waiting_for_year)
    await message.answer(get_text(lang, "search_prompt_year"))


@router.message(SearchStates.waiting_for_year)
async def process_year(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    if message.text != "/skip":
        try:
            year = int(message.text.strip())
            await state.update_data(min_year=year)
        except ValueError:
            await message.answer("⚠️ Invalid year format. Enter year like 2019 or /skip:")
            return

    await state.set_state(SearchStates.waiting_for_title)
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, "title_all"), callback_data="title:All"),
            InlineKeyboardButton(text=get_text(lang, "title_salvage"), callback_data="title:Salvage"),
            InlineKeyboardButton(text=get_text(lang, "title_clean"), callback_data="title:Clean")
        ]
    ])
    await message.answer(get_text(lang, "search_prompt_title"), reply_markup=inline_kb)


@router.callback_query(SearchStates.waiting_for_title, F.data.startswith("title:"))
async def process_title_and_execute(callback: CallbackQuery, state: FSMContext):
    title_type = callback.data.split(":")[1]
    await state.update_data(title_type=title_type)
    data = await state.get_data()
    lang = data.get("lang", "hy")

    await callback.answer()
    await callback.message.edit_text(get_text(lang, "searching"))

    filters = SearchFilter(
        make=data.get("make"),
        model=data.get("model"),
        max_budget=data.get("max_budget"),
        min_year=data.get("min_year"),
        title_type=data.get("title_type")
    )

    scraper = CopartMockScraper()
    results = await scraper.fetch_listings(filters)

    if not results:
        await callback.message.answer(get_text(lang, "no_results"))
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        cfg_repo = SystemConfigRepository(session)
        logistics_str = await cfg_repo.get_value("DEFAULT_LOGISTICS_BASE_USD", str(settings.DEFAULT_LOGISTICS_BASE_USD))
        broker_str = await cfg_repo.get_value("DEFAULT_BROKER_FEE_USD", str(settings.DEFAULT_BROKER_FEE_USD))
        logistics_val = float(logistics_str)
        broker_val = float(broker_str)

    for car in results:
        cost = CustomsCalculator.calculate_full_cost(
            auction_price=car.est_auction_price,
            year=car.year,
            engine_cc=car.engine_capacity_cc,
            fuel_type=car.fuel_type,
            base_logistics_usd=logistics_val,
            broker_fee_usd=broker_val
        )

        card_msg = get_text(
            lang,
            "car_card",
            title=car.title,
            id=car.id,
            auction_source=car.auction_source,
            year=car.year,
            mileage=car.mileage or "N/A",
            fuel_type=car.fuel_type,
            engine_cc=car.engine_capacity_cc,
            primary_damage=car.primary_damage or "N/A",
            title_type=car.title_type,
            location=car.location or "USA",
            auction_price=cost.auction_price,
            auction_fee=cost.auction_fee,
            total_logistics=cost.total_logistics,
            customs_clearance_total=cost.customs_clearance_total,
            broker_fee=cost.broker_fee,
            total_cost=cost.total_cost,
            auction_url=car.auction_url
        )
        await callback.message.answer(card_msg, parse_mode="Markdown", disable_web_page_preview=True)

    # Offer to save search as alert
    save_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_add_alert"), callback_data="save_alert_current")]
    ])
    await callback.message.answer("🔔 Want to get automatically notified when new cars like this are listed?", reply_markup=save_kb)


@router.callback_query(F.data == "save_alert_current")
async def cb_save_current_alert(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    async with AsyncSessionLocal() as session:
        repo = SavedSearchRepository(session)
        await repo.create_search(
            user_id=callback.from_user.id,
            make=data.get("make"),
            model=data.get("model"),
            max_budget=data.get("max_budget"),
            min_year=data.get("min_year"),
            title_type=data.get("title_type")
        )

    await callback.answer(get_text(lang, "save_search_success"), show_alert=True)
    await state.clear()


# --- CUSTOMS CALCULATOR STANDALONE HANDLER ---

@router.message(F.text.in_([LEXICON["hy"]["btn_calc"], LEXICON["en"]["btn_calc"]]))
async def start_calc(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        user = await repo.get_or_create(message.from_user.id)
        lang = user.language_code

    await state.update_data(lang=lang)
    await state.set_state(CalcStates.waiting_for_price)
    await message.answer(get_text(lang, "calc_prompt_price"))


@router.message(CalcStates.waiting_for_price)
async def calc_price(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    try:
        price = float(message.text.replace("$", "").strip())
        await state.update_data(price=price)
    except ValueError:
        await message.answer("⚠️ Invalid amount. Enter price e.g. 5000:")
        return

    await state.set_state(CalcStates.waiting_for_year)
    await message.answer(get_text(lang, "calc_prompt_year"))


@router.message(CalcStates.waiting_for_year)
async def calc_year(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    try:
        year = int(message.text.strip())
        await state.update_data(year=year)
    except ValueError:
        await message.answer("⚠️ Invalid year. Enter year e.g. 2020:")
        return

    await state.set_state(CalcStates.waiting_for_cc)
    await message.answer(get_text(lang, "calc_prompt_cc"))


@router.message(CalcStates.waiting_for_cc)
async def calc_cc(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "hy")
    try:
        cc = int(message.text.strip())
        await state.update_data(cc=cc)
    except ValueError:
        await message.answer("⚠️ Invalid number. Enter engine cc e.g. 2000:")
        return

    await state.set_state(CalcStates.waiting_for_fuel)
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, "fuel_gasoline"), callback_data="fuel:gasoline"),
            InlineKeyboardButton(text=get_text(lang, "fuel_hybrid"), callback_data="fuel:hybrid"),
            InlineKeyboardButton(text=get_text(lang, "fuel_electric"), callback_data="fuel:electric")
        ]
    ])
    await message.answer(get_text(lang, "calc_prompt_fuel"), reply_markup=inline_kb)


@router.callback_query(CalcStates.waiting_for_fuel, F.data.startswith("fuel:"))
async def calc_finish(callback: CallbackQuery, state: FSMContext):
    fuel_type = callback.data.split(":")[1]
    data = await state.get_data()
    lang = data.get("lang", "hy")

    async with AsyncSessionLocal() as session:
        cfg_repo = SystemConfigRepository(session)
        logistics_val = float(await cfg_repo.get_value("DEFAULT_LOGISTICS_BASE_USD", str(settings.DEFAULT_LOGISTICS_BASE_USD)))
        broker_val = float(await cfg_repo.get_value("DEFAULT_BROKER_FEE_USD", str(settings.DEFAULT_BROKER_FEE_USD)))

    cost = CustomsCalculator.calculate_full_cost(
        auction_price=data["price"],
        year=data["year"],
        engine_cc=data["cc"],
        fuel_type=fuel_type,
        base_logistics_usd=logistics_val,
        broker_fee_usd=broker_val
    )

    card_msg = get_text(
        lang,
        "car_card",
        title=f"Custom Search ({data['year']}, {fuel_type})",
        id="CALC-ONLY",
        auction_source="Manual Calc",
        year=data["year"],
        mileage="N/A",
        fuel_type=fuel_type,
        engine_cc=data["cc"],
        primary_damage="N/A",
        title_type="N/A",
        location="USA",
        auction_price=cost.auction_price,
        auction_fee=cost.auction_fee,
        total_logistics=cost.total_logistics,
        customs_clearance_total=cost.customs_clearance_total,
        broker_fee=cost.broker_fee,
        total_cost=cost.total_cost,
        auction_url="https://copart.com"
    )

    await callback.answer()
    await callback.message.edit_text(card_msg, parse_mode="Markdown")
    await state.clear()


# --- BROKER / ADMIN PANEL HANDLERS ---

@router.message(F.text.in_([LEXICON["hy"]["btn_broker_panel"], LEXICON["en"]["btn_broker_panel"]]))
async def broker_panel(message: Message):
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_or_create(message.from_user.id)
        lang = user.language_code

        cfg_repo = SystemConfigRepository(session)
        logistics_val = await cfg_repo.get_value("DEFAULT_LOGISTICS_BASE_USD", str(settings.DEFAULT_LOGISTICS_BASE_USD))
        broker_val = await cfg_repo.get_value("DEFAULT_BROKER_FEE_USD", str(settings.DEFAULT_BROKER_FEE_USD))

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_set_logistics"), callback_data="admin:set_logistics")],
        [InlineKeyboardButton(text=get_text(lang, "btn_set_broker_fee"), callback_data="admin:set_broker_fee")]
    ])

    msg = get_text(lang, "broker_panel_text", logistics_base=logistics_val, broker_fee=broker_val)
    await message.answer(msg, parse_mode="Markdown", reply_markup=inline_kb)


@router.callback_query(F.data == "admin:set_logistics")
async def cb_admin_logistics(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_logistics)
    await callback.answer()
    await callback.message.answer(get_text("hy", "prompt_new_logistics"))


@router.message(AdminStates.waiting_for_logistics)
async def process_admin_logistics(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip())
        async with AsyncSessionLocal() as session:
            cfg_repo = SystemConfigRepository(session)
            await cfg_repo.set_value("DEFAULT_LOGISTICS_BASE_USD", str(val))
        await message.answer(get_text("hy", "success_update"))
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Please enter a valid number.")


@router.callback_query(F.data == "admin:set_broker_fee")
async def cb_admin_broker_fee(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.waiting_for_broker_fee)
    await callback.answer()
    await callback.message.answer(get_text("hy", "prompt_new_broker_fee"))


@router.message(AdminStates.waiting_for_broker_fee)
async def process_admin_broker_fee(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip())
        async with AsyncSessionLocal() as session:
            cfg_repo = SystemConfigRepository(session)
            await cfg_repo.set_value("DEFAULT_BROKER_FEE_USD", str(val))
        await message.answer(get_text("hy", "success_update"))
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Please enter a valid number.")


# --- MY ALERTS HANDLER ---

@router.message(F.text.in_([LEXICON["hy"]["btn_alerts"], LEXICON["en"]["btn_alerts"]]))
async def view_alerts(message: Message):
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_or_create(message.from_user.id)
        lang = user.language_code

        search_repo = SavedSearchRepository(session)
        searches = await search_repo.get_user_searches(message.from_user.id)

    if not searches:
        await message.answer(get_text(lang, "no_saved_searches"))
        return

    for item in searches:
        text = f"🔔 **Alert #{item.id}**\n• Make: {item.make or 'All'}\n• Model: {item.model or 'All'}\n• Max Budget: ${item.max_budget or 'N/A'}\n• Min Year: {item.min_year or 'N/A'}"
        delete_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "btn_delete"), callback_data=f"del_alert:{item.id}")]
        ])
        await message.answer(text, parse_mode="Markdown", reply_markup=delete_kb)


@router.callback_query(F.data.startswith("del_alert:"))
async def cb_del_alert(callback: CallbackQuery):
    alert_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        repo = SavedSearchRepository(session)
        await repo.delete_search(alert_id, callback.from_user.id)

    await callback.answer("Deleted!")
    await callback.message.delete()
