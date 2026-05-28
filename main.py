from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from tradingview_ta import TA_Handler, Interval

import asyncio
import os

# =========================================
# BOT TOKEN
# =========================================

TOKEN = os.getenv("8242361758:AAHa14jEVgJ7_cHTxchLlJwvTL2ZfQJLKqw")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found in Railway Variables")

# =========================================
# VALID IDS
# =========================================

VALID_IDS = [
    "88141513",
    "76281922",
    "91827364"
]

# =========================================
# BOT
# =========================================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

# =========================================
# PAIRS
# =========================================

pairs = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "NZDUSD",
    "EURJPY",
    "EURGBP",
    "GBPJPY",
    "AUDJPY",
    "EURAUD"
]

# =========================================
# USER PAIR STORAGE
# =========================================

user_pair = {}

# =========================================
# PAIR KEYBOARD
# =========================================

pair_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="EURUSD"), KeyboardButton(text="GBPUSD")],
        [KeyboardButton(text="USDJPY"), KeyboardButton(text="AUDUSD")],
        [KeyboardButton(text="USDCAD"), KeyboardButton(text="USDCHF")],
        [KeyboardButton(text="NZDUSD"), KeyboardButton(text="EURJPY")],
        [KeyboardButton(text="EURGBP"), KeyboardButton(text="GBPJPY")],
        [KeyboardButton(text="AUDJPY"), KeyboardButton(text="EURAUD")]
    ],
    resize_keyboard=True
)

# =========================================
# TIMEFRAME KEYBOARD
# =========================================

time_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1min")],
        [KeyboardButton(text="5min")],
        [KeyboardButton(text="15min")],
        [KeyboardButton(text="🔙 Back")]
    ],
    resize_keyboard=True
)

# =========================================
# START
# =========================================

@dp.message(CommandStart())
async def start(message: types.Message):

    await message.answer(
        "🔐 Send Trader ID:"
    )

# =========================================
# MAIN HANDLER
# =========================================

@dp.message()
async def signals(message: types.Message):

    text = message.text.upper()

    # =====================================
    # BACK BUTTON
    # =====================================

    if text == "🔙 BACK":

        await message.answer(
            "📊 Select Pair:",
            reply_markup=pair_keyboard
        )

        return

    # =====================================
    # VERIFY ID
    # =====================================

    if text.isdigit():

        if text in VALID_IDS:

            await message.answer(
                "✅ Verification Successful\n\n📊 Select Pair:",
                reply_markup=pair_keyboard
            )

        else:

            await message.answer(
                "❌ Invalid Trader ID\n\n"
                "📌 Create account first.\n"
                "🔗 https://broker-qx.pro/sign-up/?lid=1672051\n\n"
                "📩 Message on @Arntrader"
            )

        return

    # =====================================
    # PAIR SELECT
    # =====================================

    if text in pairs:

        user_pair[message.chat.id] = text

        await message.answer(
            "⏰ Select Timeframe:",
            reply_markup=time_keyboard
        )

        return

    # =====================================
    # TIMEFRAME
    # =====================================

    if text in ["1MIN", "5MIN", "15MIN"]:

        pair = user_pair.get(message.chat.id)

        if not pair:

            await message.answer(
                "❌ Select Pair First"
            )

            return

        try:

            # =================================
            # INTERVAL
            # =================================

            if text == "1MIN":

                interval = Interval.INTERVAL_1_MINUTE

            elif text == "5MIN":

                interval = Interval.INTERVAL_5_MINUTES

            else:

                interval = Interval.INTERVAL_15_MINUTES

            # =================================
            # ANALYSIS
            # =================================

            handler = TA_Handler(
                symbol=pair,
                screener="forex",
                exchange="FX_IDC",
                interval=interval
            )

            analysis = handler.get_analysis()

            summary = analysis.summary
            indicators = analysis.indicators

            buy = summary.get("BUY", 0)
            sell = summary.get("SELL", 0)
            neutral = summary.get("NEUTRAL", 0)

            rsi = round(indicators.get("RSI", 0), 2)

            macd = round(indicators.get("MACD.macd", 0), 4)
            macd_signal = round(indicators.get("MACD.signal", 0), 4)

            ema10 = round(indicators.get("EMA10", 0), 4)
            ema20 = round(indicators.get("EMA20", 0), 4)
            ema50 = round(indicators.get("EMA50", 0), 4)

            # =================================
            # STRATEGY
            # =================================

            signal = "WAIT"
            trend = "NEUTRAL"
            strength = "WEAK"

            # STRONG BUY

            if (
                buy >= 12
                and buy > sell
                and rsi >= 50
                and ema10 > ema20
            ):

                signal = "UP"
                trend = "BUY"
                strength = "STRONG BUY"

            # STRONG SELL

            elif (
                sell >= 12
                and sell > buy
                and rsi <= 50
                and ema10 < ema20
            ):

                signal = "DOWN"
                trend = "SELL"
                strength = "STRONG SELL"

            # MEDIUM BUY

            elif buy > sell and rsi >= 50:

                signal = "UP"
                trend = "BUY"
                strength = "MEDIUM BUY"

            # MEDIUM SELL

            elif sell > buy and rsi <= 50:

                signal = "DOWN"
                trend = "SELL"
                strength = "MEDIUM SELL"

            # =================================
            # EMOJI
            # =================================

            if signal == "UP":

                emoji = "🟢"

            elif signal == "DOWN":

                emoji = "🔴"

            else:

                emoji = "🟡"

            # =================================
            # RESULT
            # =================================

            result = f"""
{emoji} <b>SIGNAL : {signal}</b>

📊 <b>PAIR:</b> {pair}

⏰ <b>TIMEFRAME:</b> {text}

📈 <b>LIVE MARKET ANALYSIS</b>

🟢 BUY: {buy}
🔴 SELL: {sell}
🟡 NEUTRAL: {neutral}

📌 TREND: {trend}

📊 RSI: {rsi}

📉 MACD: {macd}
📈 MACD SIGNAL: {macd_signal}

📌 EMA10: {ema10}
📌 EMA20: {ema20}
📌 EMA50: {ema50}

🔥 STRENGTH: {strength}
"""

            await message.answer(result)

        except Exception as e:

            await message.answer(
                f"❌ Error:\n{e}"
            )

# =========================================
# MAIN
# =========================================

async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    asyncio.run(main())