import re
import sqlite3
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

router = Router()
DB_PATH = "contractors.db"  # Путь к SQLite базе данных

# --- Клавиатуры ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сделать заказ")],
        [KeyboardButton(text="Узнать наличие товара")]
    ],
    resize_keyboard=True
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться назад")]],
    resize_keyboard=True
)

confirm_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="ДА"), KeyboardButton(text="НЕТ")]],
    resize_keyboard=True
)

error_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться назад")]
    ],
    resize_keyboard=True
)

# --- Простая система состояний ---
user_states = {}  # user_id -> состояние


# --- Поиск контрагента по ИНН ---
def find_contractor_by_inn(inn: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM contractors WHERE inn = ?", (inn,))
        row = cursor.fetchone()
        return row[1] if row else None
    except Exception as e:
        return None
    finally:
        conn.close()


# --- Обработчики ---

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_states[message.from_user.id] = None
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu)


@router.message(F.text == "Сделать заказ")
async def make_order(message: Message):
    user_states[message.from_user.id] = "waiting_for_inn"
    await message.answer("Введите свой ИНН:", reply_markup=back_menu)


@router.message(F.text == "Узнать наличие товара")
async def check_stock(message: Message):
    await message.answer("Узнать наличие товара", reply_markup=back_menu)


@router.message(F.text == "Вернуться назад")
async def go_back(message: Message):
    user_states[message.from_user.id] = None
    await message.answer("Вы вернулись в главное меню", reply_markup=main_menu)


@router.message(F.text == "ДА")
async def confirm_data(message: Message):
    await message.answer("Отлично!", reply_markup=main_menu)
    user_states[message.from_user.id] = None


@router.message(F.text == "НЕТ")
async def deny_data(message: Message):
    user_states[message.from_user.id] = "waiting_for_inn"
    await message.answer("Введите ИНН повторно:", reply_markup=back_menu)


@router.message()
async def process_inn(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state == "waiting_for_inn":
        inn = message.text.strip()

        # Валидация ИНН
        if not re.fullmatch(r"\d{10}|\d{12}", inn):
            await message.answer(
                "Введено некорректное значение. Введите ИНН, состоящий из 10 или 12 цифр.",
                reply_markup=error_menu
            )
            return

        # Поиск по базе
        contractor_name = find_contractor_by_inn(inn)

        if contractor_name:
            await message.answer(
                f"Контрагент с ИНН {inn} найден: {contractor_name}. Это вы?",
                reply_markup=confirm_menu
            )
            user_states[user_id] = "confirm_inn"
        else:
            await message.answer(
                f"ИНН {inn} не найден в базе. Пожалуйста, введите корректный ИНН или вернитесь назад.",
                reply_markup=error_menu
            )

    else:
        await message.answer("Пожалуйста, выберите действие из меню.", reply_markup=main_menu)