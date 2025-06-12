import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN        = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")          # e.g. https://tvuj-bot.onrender.com
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL  = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp  = Dispatcher()

# --- 1) /start handler ---
@dp.message(CommandStart())
async def send_menu(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⭐ 50 звёзд"),
                KeyboardButton(text="⭐ 100 звёзд"),
                KeyboardButton(text="⭐ 200 звёзд"),
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Привет! Добро пожаловать в наш Telegram Stars бот!\n"
        "Мы продаём звёзды по самым низким ценам!\n\n"
        "Выберите нужное количество 👇",
        reply_markup=keyboard
    )

# --- 2) Všechny ostatní zprávy ---
@dp.message()
async def handle_messages(message: Message):
    text = (message.text or "").strip()

    # výběr balíčku
    if text.startswith("⭐"):
        try:
            count = int(text.split()[1])
            price = round(count * 1.8 + 5)
            await message.answer(
                f"✅ Вы выбрали: {count} звёзд\n"
                f"💸 Цена: {price}₽\n"
                f"(Plati.Market: 1.8₽ × {count} + 5₽ комиссия)\n\n"
                "🔁 Оплатите через СБП (ВТБ) на номер:\n"
                "<b>+8 950 039 3214</b>\n\n"
                "📝 После оплаты, отправьте сообщение: <b>ОПЛАЧЕНО ✅</b>",
                parse_mode="HTML"
            )
        except:
            await message.answer("❌ Ошибка при обработке количества звёзд.")
        return

    # potvrzení platby
    if text == "ОПЛАЧЕНО ✅":
        await message.answer(
            "📸 Пожалуйста, отправьте скриншот оплаты.\n\n"
            "Затем напишите в Telegram: @wellbinuk и отправьте туда:\n\n"
            "<pre>\n"
            "ИНФО ОТ БОТА\n"
            "Количество звёзд: [УКАЗАТЬ]\n"
            "Сайт: Plati.Market\n"
            "</pre>",
            parse_mode="HTML"
        )
        return

    # případný screenshot
    if message.photo:
        await message.answer(
            "✅ Спасибо! Ваш заказ скоро будет обработан.\n"
            "Ожидайте ответа от @wellbinuk."
        )
        return

    # fallback
    await message.answer("❓ Пожалуйста, выберите количество звёзд или следуйте инструкциям.")

# --- Webhook setup & aiohttp app ---
async def on_startup(app: web.Application):
    # smažeme starý a nastavíme nový webhook
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

def create_app() -> web.Application:
    app = web.Application()
    # zaregistrujeme webhook route
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    web.run_app(create_app(), host="0.0.0.0", port=port)
