import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import urllib.request
import json

# === SOZLAMALAR ===
TELEGRAM_TOKEN = "8798149308:AAEm_Ls3qyQ63lOcXH8vzUeDOtSD_pKZshM"
WEATHER_API_KEY = "501c16a296be1c368b4865b05b6a1994"
ADMIN_USERNAME = "Burxon_Xayrullayev"

logging.basicConfig(level=logging.INFO)

user_states = {}

# =====================
# YORDAMCHI FUNKSIYALAR
# =====================

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        temp = round(data["main"]["temp"])
        feels = round(data["main"]["feels_like"])
        humidity = data["main"]["humidity"]
        wind = round(data["wind"]["speed"])
        desc = data["weather"][0]["description"].capitalize()
        return f"🌤 *{city}* ob-havosi:\n🌡 Harorat: +{temp}°C (his: +{feels}°C)\n💧 Namlik: {humidity}%\n💨 Shamol: {wind} m/s\n📋 {desc}"
    except:
        return "❌ Shahar topilmadi. To'g'ri yozing, masalan: Toshkent, Buxoro"

def get_currency():
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        result = "💰 *Valyuta kurslari (CBU):*\n\n"
        for item in data:
            if item["Ccy"] in ["USD", "EUR", "RUB"]:
                emoji = "🇺🇸" if item["Ccy"] == "USD" else "🇪🇺" if item["Ccy"] == "EUR" else "🇷🇺"
                result += f"{emoji} {item['Ccy']}: {float(item['Rate']):.2f} so'm\n"
        return result
    except:
        return "❌ Kurs ma'lumotlarini olishda xatolik"

def get_news():
    news = [
        "🔥 Toshkent shahri yangi arxitektura loyihasi e'lon qilindi",
        "🏗 O'zbekistonda 1000 ta yangi uy qurilishi boshlanadi",
        "🎓 UBS universiteti yangi yo'nalishlar ochdi",
        "💻 IT sohasida yangi imkoniyatlar: 500 ta ish o'rni",
        "🌿 Buxoroda yangi ko'kalamzorlashtirish loyihasi",
    ]
    result = "📰 *Bugungi yangiliklar:*\n\n"
    for i, n in enumerate(news[:5], 1):
        result += f"{i}. {n}\n\n"
    return result

def get_music():
    songs = [
        "🎵 Shaxnoza Otaboyeva — Yoningda",
        "🎵 Ulug'bek Rahmatullayev — Sensiz",
        "🎵 Dilnoza Yusupova — Aziz",
        "🎵 Zafarbek Qodirov — Qorakoʻzim",
        "🎵 Xurshid Rasulov — Yoqimli",
        "🎵 Bahrom — Muhabbat",
        "🎵 Nodira Pirmatova — Sog'indim",
        "🎵 Jasur Umirov — Alvido",
        "🎵 Sevinch Mo'minova — Yor-yor",
        "🎵 Elmurod Husanov — Ona",
    ]
    result = "🎵 *Eng yangi hit taronalar:*\n\n"
    for s in songs:
        result += f"{s}\n"
    return result

# =====================
# ARXITEKTURA KALKULYATOR
# =====================

def calc_maydon(uzunlik, kenglik):
    maydon = uzunlik * kenglik
    return (
        f"📐 *Maydon hisoblash:*\n\n"
        f"📏 Uzunlik: {uzunlik} m\n"
        f"📏 Kenglik: {kenglik} m\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ Maydon: *{maydon:.2f} m²*"
    )

def calc_gisht(uzunlik, kenglik, balandlik):
    devor_maydoni = 2 * (uzunlik + kenglik) * balandlik
    gisht_soni = devor_maydoni * 51  # 1 m² uchun ~51 ta g'isht
    return (
        f"🧱 *G'isht hisoblash:*\n\n"
        f"📏 Uzunlik: {uzunlik} m\n"
        f"📏 Kenglik: {kenglik} m\n"
        f"📏 Balandlik: {balandlik} m\n"
        f"━━━━━━━━━━━━━━\n"
        f"🏠 Devor maydoni: *{devor_maydoni:.2f} m²*\n"
        f"✅ G'isht miqdori: *{int(gisht_soni)} dona*\n"
        f"📦 Taxminan: *{int(gisht_soni/500)+1} pallet*"
    )

def calc_boyoq(maydon):
    boyoq = maydon / 10  # 1 litr = 10 m²
    return (
        f"🎨 *Bo'yoq hisoblash:*\n\n"
        f"📐 Maydon: {maydon} m²\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ Bo'yoq miqdori: *{boyoq:.1f} litr*\n"
        f"🪣 Taxminan: *{int(boyoq/4)+1} banka (4L)*"
    )

def calc_plitka(uzunlik, kenglik, plitka_o, plitka_k):
    xona_maydon = uzunlik * kenglik
    plitka_maydon = (plitka_o / 100) * (plitka_k / 100)
    plitka_soni = xona_maydon / plitka_maydon * 1.1  # 10% zaxira
    return (
        f"🔲 *Plitka hisoblash:*\n\n"
        f"📐 Xona: {uzunlik}m × {kenglik}m = {xona_maydon:.2f} m²\n"
        f"🔲 Plitka: {plitka_o}cm × {plitka_k}cm\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ Plitka soni: *{int(plitka_soni)} dona*\n"
        f"📦 (+10% zaxira hisobida)"
    )

def calc_narx(maydon, narx_m2):
    jami = maydon * narx_m2
    return (
        f"💰 *Qurilish narxi:*\n\n"
        f"📐 Maydon: {maydon} m²\n"
        f"💵 1 m² narxi: {narx_m2:,} so'm\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ Jami narx: *{jami:,.0f} so'm*\n"
        f"💵 ≈ *${jami/12900:.0f}*"
    )

# =====================
# BUYRUQLAR
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌤 Ob-havo", callback_data="havo"),
         InlineKeyboardButton("💰 Kurs", callback_data="kurs")],
        [InlineKeyboardButton("📰 Yangiliklar", callback_data="news"),
         InlineKeyboardButton("🎵 Musiqa", callback_data="music")],
        [InlineKeyboardButton("📐 Arxitektura Kalkulyator", callback_data="kalkulator")],
        [InlineKeyboardButton("🎨 Dizayn", callback_data="dizayn"),
         InlineKeyboardButton("👨‍💼 Admin", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 *Yaratuvchi Bot* ga xush kelibsiz!\n\n"
        "Quyidagi xizmatlardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "havo":
        user_states[user_id] = "waiting_city"
        await query.message.reply_text("📍 Shahar nomini yozing:")

    elif data == "kurs":
        result = get_currency()
        await query.message.reply_text(result, parse_mode="Markdown")

    elif data == "news":
        result = get_news()
        await query.message.reply_text(result, parse_mode="Markdown")

    elif data == "music":
        result = get_music()
        await query.message.reply_text(result, parse_mode="Markdown")

    elif data == "admin":
        keyboard = [[InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "👨‍💼 *Admin bilan bog'lanish:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "kalkulator":
        keyboard = [
            [InlineKeyboardButton("📏 Maydon hisoblash", callback_data="calc_maydon")],
            [InlineKeyboardButton("🧱 G'isht miqdori", callback_data="calc_gisht")],
            [InlineKeyboardButton("🎨 Bo'yoq miqdori", callback_data="calc_boyoq")],
            [InlineKeyboardButton("🔲 Plitka miqdori", callback_data="calc_plitka")],
            [InlineKeyboardButton("💰 Qurilish narxi", callback_data="calc_narx")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📐 *Arxitektura Kalkulyatori*\n\nNimani hisoblaysiz?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "calc_maydon":
        user_states[user_id] = "calc_maydon_1"
        await query.message.reply_text("📏 Xona uzunligini yozing (metrda, masalan: 5.5):")

    elif data == "calc_gisht":
        user_states[user_id] = "calc_gisht_1"
        context.user_data["calc"] = {}
        await query.message.reply_text("🧱 Bino uzunligini yozing (metrda):")

    elif data == "calc_boyoq":
        user_states[user_id] = "calc_boyoq_1"
        await query.message.reply_text("🎨 Bo'yaladigan maydonni yozing (m²):")

    elif data == "calc_plitka":
        user_states[user_id] = "calc_plitka_1"
        context.user_data["calc"] = {}
        await query.message.reply_text("🔲 Xona uzunligini yozing (metrda):")

    elif data == "calc_narx":
        user_states[user_id] = "calc_narx_1"
        context.user_data["calc"] = {}
        await query.message.reply_text("💰 Qurilish maydonini yozing (m²):")

    elif data == "dizayn":
        keyboard = [
            [InlineKeyboardButton("🎴 Vizitka", callback_data="dizayn_vizitka")],
            [InlineKeyboardButton("🏛 Arxitektura g'oyalar", callback_data="dizayn_arch")],
            [InlineKeyboardButton("📱 Banner maslahat", callback_data="dizayn_banner")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🎨 Qanday dizayn kerak?", reply_markup=reply_markup)

    elif data == "dizayn_vizitka":
        user_states[user_id] = "dizayn_vizitka_name"
        context.user_data["dizayn"] = {}
        await query.message.reply_text("🎴 Ism familiyangizni yozing:")

    elif data == "dizayn_arch":
        await query.message.reply_text(
            "🏛 *Arxitektura dizayn g'oyalari:*\n\n"
            "1. Minimalist — oq va kulrang\n"
            "2. Zamonaviy — shisha va metall\n"
            "3. Klassik — ustunlar va gumbazlar\n"
            "4. Ekologik — yashil o'simliklar\n"
            "5. Industrial — g'isht va beton",
            parse_mode="Markdown"
        )

    elif data == "dizayn_banner":
        await query.message.reply_text(
            "📱 *Banner o'lchamlari:*\n\n"
            "📐 Facebook: 1200x628 px\n"
            "📐 Instagram: 1080x1080 px\n"
            "📐 Twitter: 1500x500 px",
            parse_mode="Markdown"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_states.get(user_id, "")

    try:
        # Ob-havo
        if state == "waiting_city":
            result = get_weather(text)
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # Maydon hisoblash
        elif state == "calc_maydon_1":
            context.user_data["calc"] = {"uzunlik": float(text)}
            user_states[user_id] = "calc_maydon_2"
            await update.message.reply_text("📏 Xona kengligini yozing (metrda):")

        elif state == "calc_maydon_2":
            uzunlik = context.user_data["calc"]["uzunlik"]
            kenglik = float(text)
            result = calc_maydon(uzunlik, kenglik)
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # G'isht hisoblash
        elif state == "calc_gisht_1":
            context.user_data["calc"]["uzunlik"] = float(text)
            user_states[user_id] = "calc_gisht_2"
            await update.message.reply_text("🧱 Bino kengligini yozing (metrda):")

        elif state == "calc_gisht_2":
            context.user_data["calc"]["kenglik"] = float(text)
            user_states[user_id] = "calc_gisht_3"
            await update.message.reply_text("🧱 Devor balandligini yozing (metrda):")

        elif state == "calc_gisht_3":
            uzunlik = context.user_data["calc"]["uzunlik"]
            kenglik = context.user_data["calc"]["kenglik"]
            balandlik = float(text)
            result = calc_gisht(uzunlik, kenglik, balandlik)
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # Bo'yoq hisoblash
        elif state == "calc_boyoq_1":
            result = calc_boyoq(float(text))
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # Plitka hisoblash
        elif state == "calc_plitka_1":
            context.user_data["calc"]["uzunlik"] = float(text)
            user_states[user_id] = "calc_plitka_2"
            await update.message.reply_text("🔲 Xona kengligini yozing (metrda):")

        elif state == "calc_plitka_2":
            context.user_data["calc"]["kenglik"] = float(text)
            user_states[user_id] = "calc_plitka_3"
            await update.message.reply_text("🔲 Plitka uzunligini yozing (sm, masalan: 60):")

        elif state == "calc_plitka_3":
            context.user_data["calc"]["plitka_o"] = float(text)
            user_states[user_id] = "calc_plitka_4"
            await update.message.reply_text("🔲 Plitka kengligini yozing (sm, masalan: 60):")

        elif state == "calc_plitka_4":
            uzunlik = context.user_data["calc"]["uzunlik"]
            kenglik = context.user_data["calc"]["kenglik"]
            plitka_o = context.user_data["calc"]["plitka_o"]
            plitka_k = float(text)
            result = calc_plitka(uzunlik, kenglik, plitka_o, plitka_k)
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # Narx hisoblash
        elif state == "calc_narx_1":
            context.user_data["calc"]["maydon"] = float(text)
            user_states[user_id] = "calc_narx_2"
            await update.message.reply_text("💰 1 m² qurilish narxini yozing (so'mda, masalan: 2500000):")

        elif state == "calc_narx_2":
            maydon = context.user_data["calc"]["maydon"]
            narx = float(text)
            result = calc_narx(maydon, narx)
            await update.message.reply_text(result, parse_mode="Markdown")
            user_states.pop(user_id, None)

        # Vizitka
        elif state == "dizayn_vizitka_name":
            context.user_data["dizayn"]["name"] = text
            user_states[user_id] = "dizayn_vizitka_title"
            await update.message.reply_text("💼 Lavozimingizni yozing:")

        elif state == "dizayn_vizitka_title":
            context.user_data["dizayn"]["title"] = text
            user_states[user_id] = "dizayn_vizitka_phone"
            await update.message.reply_text("📞 Telefon raqamingizni yozing:")

        elif state == "dizayn_vizitka_phone":
            context.user_data["dizayn"]["phone"] = text
            dizayn = context.user_data["dizayn"]
            vizitka = f"┌─────────────────────────┐\n│  {dizayn['name']}\n│  {dizayn['title']}\n│  📞 {dizayn['phone']}\n└─────────────────────────┘"
            await update.message.reply_text(f"✅ *Vizitkaingiz:*\n```{vizitka}```", parse_mode="Markdown")
            user_states.pop(user_id, None)

        else:
            await update.message.reply_text("Menyu uchun /start yozing! 😊")

    except ValueError:
        await update.message.reply_text("❌ Raqam kiriting! Masalan: 5 yoki 5.5")

def main():
    print("🤖 Yaratuvchi Bot ishga tushmoqda...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
