import os
import logging
import datetime
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
from utils import get_altseason_index, get_btc_dominance, get_btc_price

# Загружаем токен из переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# Создаем меню клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard.add(
KeyboardButton("💸Индекс\nальтсезона💸"),
KeyboardButton("💰Курс BTC💰"),
KeyboardButton("📊Доминация BTC📊"),
KeyboardButton("🎮Играть🎮")
               )

# Словарь для хранения состояния игры
user_games = {}

@dp.message_handler(commands=["start", "index"])
async def send_welcome(message: Message):
    """Приветственное сообщение с кнопками"""
    await message.answer("Привет! Нажми кнопку, чтобы узнать информацию по рынку или сыграть в игру.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "💸Индекс\nальтсезона💸")
async def send_altseason_index(message: Message):
    """Отправляет пользователю индекс альтсезона"""
    time, index = get_altseason_index()
    if index is not None:
        date = datetime.datetime.strptime(time, "%Y-%m-%d").strftime("%d.%m.%y")
        
        if 1 <= index < 25:
            season = "🤯Ну, хуже уже не будет и бац бац бац-бац-бац и Биткоин-сезон🤯"
        elif 25 <= index < 75:
            season = "Хуевое💩, а это значит что ты бич"
        else:
            season = "Альтсезон"
        
        text = f"Сегодня {date}\nИндекс альтсезона: {index}%\nСостояние рынка: {season}"
    else:
        text = "Не удалось получить данные за сегодняшний день. Попробуйте позже."
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📊Доминация BTC📊")
async def send_btc_dominance(message: Message):
    """Отправляет пользователю доминацию BTC"""
    dominance = get_btc_dominance()
    if dominance:
        text = f"📊 Доминация BTC: {dominance}"
    else:
        text = "Не удалось получить данные о доминации BTC. Попробуйте позже."
    
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "🎮Играть🎮")
async def start_game(message: Message):
    """Начинает игру 'Угадай число'"""
    user_id = message.from_user.id
    number_to_guess = random.randint(1, 100)
    user_games[user_id] = {"number": number_to_guess, "attempts": 0}
    
    await message.answer("Я загадал число от 1 до 100. Попробуй угадать!")

@dp.message_handler(lambda message: message.from_user.id in user_games)
async def play_game(message: Message):
    """Обрабатывает ход игры"""
    user_id = message.from_user.id
    game_data = user_games.get(user_id)

    if not game_data:
        return

    try:
        guess = int(message.text)
        game_data["attempts"] += 1

        if guess < game_data["number"]:
            await message.answer("Слишком маленькое! Попробуй еще раз.")
        elif guess > game_data["number"]:
            await message.answer("Слишком большое! Попробуй еще раз.")
        else:
            attempts = game_data["attempts"]
            await message.answer(f"🎉 Поздравляю! Ты угадал число за {attempts} попыток! 🎉")
            del user_games[user_id]
    except ValueError:
        await message.answer("Пожалуйста, введи целое число.")
        
@dp.message_handler(lambda message: message.text == "💰Курс BTC💰")
async def send_btc_price(message: Message):
    """Отправляет пользователю текущий курс BTC"""
    price = get_btc_price()
    if price:
        text = f"💰 Курс BTC - {price:,} USDT".replace(",", ".")
    else:
        text = "Не удалось получить курс BTC. Попробуйте позже."
    
    await message.answer(text)
    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
