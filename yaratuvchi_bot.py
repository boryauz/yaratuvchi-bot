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
        return "❌ Shahar topilmadi. To'g'ri yozing, masalan: Toshkent, Buxoro, Samarqand"

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
        "🚀 O'zbekiston texnologiyalar forumi 2026 e'lon qilindi",
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

portfolio_templates = {
    "minimal": "╔══════════════════════╗\n║ {name}\n║ {title}\n╚══════════════════════╝\n\n📞 {phone}\n📧 {email}\n📍 {city}\n\n🛠 Ko'nikmalar:\n{skills}\n\n📁 Loyihalar:\n{projects}",
    "modern": "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n  {name}\n  {title}\n▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n\n📱 {phone} | 📧 {email}\n📍 {city}\n\n⚡ {skills}\n\n🏆 Loyihalar:\n{projects}",
    "classic": "━━━━━━━━━━━━━━━━━━━━\n        {name}\n     {title}\n━━━━━━━━━━━━━━━━━━━━\nTelefon: {phone}\nEmail: {email}\nShahar: {city}\n\nBilimlar: {skills}\n\nIshlar:\n{projects}\n━━━━━━━━━━━━━━━━━━━━"
}

# =====================
# BUYRUQLAR
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌤 Ob-havo", callback_data="havo"),
         InlineKeyboardButton("💰 Kurs", callback_data="kurs")],
        [InlineKeyboardButton("📰 Yangiliklar", callback_data="news"),
         InlineKeyboardButton("🎵 Musiqa", callback_data="music")],
        [InlineKeyboardButton("📋 Portfolio", callback_data="portfolio"),
         InlineKeyboardButton("🎨 Dizayn", callback_data="dizayn")],
        [InlineKeyboardButton("👨‍💼 Admin bilan bog'lanish", callback_data="admin")],
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
        await query.message.reply_text("📍 Shahar nomini yozing (masalan: Toshkent, Buxoro):")

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
            "👨‍💼 *Admin bilan bog'lanish*\n\n"
            "Savollaringiz bo'lsa admin bilan bog'laning:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "portfolio":
        user_states[user_id] = "portfolio_name"
        context.user_data["portfolio"] = {}
        await query.message.reply_text("📋 *Portfolio yaratish*\n\nIsm va familiyangizni yozing:", parse_mode="Markdown")

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
        context.user_data["dizayn"] = {"type": "vizitka"}
        await query.message.reply_text("🎴 *Vizitka yaratish*\n\nIsm familiyangizni yozing:", parse_mode="Markdown")

    elif data == "dizayn_arch":
        await query.message.reply_text(
            "🏛 *Arxitektura dizayn g'oyalari:*\n\n"
            "1. Minimalist — oq va kulrang ranglar\n"
            "2. Zamonaviy — shisha va metall\n"
            "3. Klassik — ustunlar va gumbazlar\n"
            "4. Ekologik — yashil o'simliklar bilan\n"
            "5. Industrial — g'isht va beton\n\n"
            "💡 Batafsil maslahat uchun adminga murojaat qiling!",
            parse_mode="Markdown"
        )

    elif data == "dizayn_banner":
        await query.message.reply_text(
            "📱 *Banner dizayn maslahatlari:*\n\n"
            "📐 Facebook: 1200x628 px\n"
            "📐 Instagram: 1080x1080 px\n"
            "📐 Twitter: 1500x500 px\n\n"
            "🎨 Rang sxemasi:\n"
            "• Ko'k + Oq = Professional\n"
            "• Qora + Oltin = Luxus\n"
            "• Yashil + Oq = Ekologik\n\n"
            "💡 Batafsil maslahat uchun adminga murojaat qiling!",
            parse_mode="Markdown"
        )

    elif data.startswith("portfolio_template_"):
        template_name = data.replace("portfolio_template_", "")
        portfolio = context.user_data.get("portfolio", {})
        template = portfolio_templates.get(template_name, portfolio_templates["minimal"])
        projects_text = ""
        for i, p in enumerate(portfolio.get("projects", []), 1):
            projects_text += f"{i}. {p}\n"
        result = template.format(
            name=portfolio.get("name", ""),
            title=portfolio.get("title", ""),
            phone=portfolio.get("phone", ""),
            email=portfolio.get("email", ""),
            city=portfolio.get("city", ""),
            skills=portfolio.get("skills", ""),
            projects=projects_text
        )
        await query.message.reply_text(f"✅ *Sizning portfoliongiz:*\n```{result}```", parse_mode="Markdown")
        user_states.pop(user_id, None)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_states.get(user_id, "")

    if state == "waiting_city":
        result = get_weather(text)
        await update.message.reply_text(result, parse_mode="Markdown")
        user_states.pop(user_id, None)

    elif state == "portfolio_name":
        context.user_data["portfolio"]["name"] = text
        user_states[user_id] = "portfolio_title"
        await update.message.reply_text("💼 Mutaxassisligingizni yozing (masalan: Arxitektor):")

    elif state == "portfolio_title":
        context.user_data["portfolio"]["title"] = text
        user_states[user_id] = "portfolio_phone"
        await update.message.reply_text("📞 Telefon raqamingizni yozing:")

    elif state == "portfolio_phone":
        context.user_data["portfolio"]["phone"] = text
        user_states[user_id] = "portfolio_email"
        await update.message.reply_text("📧 Email manzilingizni yozing:")

    elif state == "portfolio_email":
        context.user_data["portfolio"]["email"] = text
        user_states[user_id] = "portfolio_city"
        await update.message.reply_text("📍 Shahringizni yozing:")

    elif state == "portfolio_city":
        context.user_data["portfolio"]["city"] = text
        user_states[user_id] = "portfolio_skills"
        await update.message.reply_text("🛠 Ko'nikmalaringizni yozing (masalan: AutoCAD, 3Ds Max, Corona):")

    elif state == "portfolio_skills":
        context.user_data["portfolio"]["skills"] = text
        user_states[user_id] = "portfolio_projects"
        context.user_data["portfolio"]["projects"] = []
        await update.message.reply_text("📁 Loyihalaringizni yozing (har birini alohida, tugatish uchun 'tayyor' yozing):")

    elif state == "portfolio_projects":
        if text.lower() == "tayyor":
            keyboard = [
                [InlineKeyboardButton("🎯 Minimal", callback_data="portfolio_template_minimal")],
                [InlineKeyboardButton("⚡ Modern", callback_data="portfolio_template_modern")],
                [InlineKeyboardButton("📜 Klassik", callback_data="portfolio_template_classic")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("🎨 Shablon tanlang:", reply_markup=reply_markup)
        else:
            context.user_data["portfolio"]["projects"].append(text)
            await update.message.reply_text(f"✅ Qo'shildi! Yana loyiha qo'shing yoki 'tayyor' yozing.")

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
