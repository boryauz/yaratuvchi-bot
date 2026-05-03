import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import urllib.request
import json
import math

# === SOZLAMALAR ===
TELEGRAM_TOKEN = "8798149308:AAEm_Ls3qyQ63lOcXH8vzUeDOtSD_pKZshM"
WEATHER_API_KEY = "501c16a296be1c368b4865b05b6a1994"
ADMIN_USERNAME = "Burxon_Xayrullayev"

logging.basicConfig(level=logging.INFO)
user_states = {}

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌤 Ob-havo", callback_data="havo"),
         InlineKeyboardButton("💰 Kurs", callback_data="kurs")],
        [InlineKeyboardButton("🏠 Qurilish kalkulyator", callback_data="qurilish")],
        [InlineKeyboardButton("📐 Arxitektura kalkulyator", callback_data="arxitektura")],
        [InlineKeyboardButton("👨‍💼 Admin", callback_data="admin")],
    ])

def back_to_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
    ])

def back_to_qurilish():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="qurilish")]
    ])

def done_qurilish():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="qurilish"),
         InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]
    ])

def back_to_arxitektura():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="arxitektura")]
    ])

def done_arxitektura():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="arxitektura"),
         InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]
    ])

def result_keyboard(back_to):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data=back_to),
         InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]
    ])

# =====================
# OB-HAVO VA KURS
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
        return "❌ Shahar topilmadi. Masalan: Toshkent, Buxoro"

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

# =====================
# QURILISH KALKULYATOR
# =====================

def calc_maydon(u, k): return f"📐 *Maydon:*\n{u}m × {k}m = *{u*k:.2f} m²*"
def calc_yuza_q(u, k, b): return f"🏠 *Uy yuzasi:*\nUzunlik: {u}m | Kenglik: {k}m | Balandlik: {b}m\n━━━━━━━━━━━\n📐 Pol: *{u*k:.2f} m²*\n🏠 Devorlar: *{2*(u+k)*b:.2f} m²*\n🔝 Shift: *{u*k:.2f} m²*\n✅ Jami: *{u*k*2 + 2*(u+k)*b:.2f} m²*"
def calc_gisht(u, k, b):
    d = 2*(u+k)*b
    g = int(d*51)
    return f"🧱 *G'isht:*\nDevor: {d:.2f} m²\n✅ *{g} dona* (~{g//500+1} pallet)"
def calc_boyoq(m): return f"🎨 *Bo'yoq:*\n{m} m² uchun\n✅ *{m/10:.1f} litr* (~{int(m/10/4)+1} banka)"
def calc_plitka(u, k, po, pk):
    xm = u*k
    pm = (po/100)*(pk/100)
    soni = int(xm/pm*1.1)
    return f"🔲 *Plitka:*\nXona: {xm:.2f} m² | Plitka: {po}×{pk} sm\n✅ *{soni} dona* (+10% zaxira)"
def calc_narx(m, n):
    j = m*n
    return f"💰 *Qurilish narxi:*\n{m} m² × {n:,} so'm\n✅ *{j:,.0f} so'm*\n≈ *${j/12900:.0f}*"
def calc_deraza(u, k, d_soni, e_soni):
    devor = 2*(u+k)*k
    d_mayd = d_soni * 1.5
    e_mayd = e_soni * 2.0
    sof = devor - d_mayd - e_mayd
    return f"🪟 *Deraza va eshik:*\nDevor: {devor:.2f} m²\nDerazalar: {d_soni} ta (~{d_mayd} m²)\nEshiklar: {e_soni} ta (~{e_mayd} m²)\n✅ Sof devor: *{sof:.2f} m²*"
def calc_sement(m):
    sement = m * 0.3
    qum = m * 1.0
    shag = m * 1.2
    return f"🏗 *Sement:*\n{m} m² uchun:\n✅ Sement: *{sement:.1f} qop (50kg)*\n✅ Qum: *{qum:.1f} m³*\n✅ Shag'al: *{shag:.1f} m³*"
def calc_temir(u, k, b):
    hajm = u*k*b
    temir = hajm * 100
    beton = hajm * 1.5
    return f"🔩 *Temir-beton:*\nHajm: {hajm:.2f} m³\n✅ Temir: *{temir:.0f} kg*\n✅ Beton: *{beton:.2f} m³*"

# =====================
# ARXITEKTURA KALKULYATOR
# =====================

def calc_perimetr(u, k): return f"📏 *Perimetr:*\n{u}m × {k}m\n✅ P = 2×({u}+{k}) = *{2*(u+k):.2f} m*"
def calc_yuza_a(u, k, b):
    pol = u * k
    devor = 2 * (u + k) * b
    shift = u * k
    jami = pol + devor + shift
    return f"📐 *To'liq yuza:*\nUzunlik: {u}m | Kenglik: {k}m | Balandlik: {b}m\n━━━━━━━━━━━\n📐 Pol: *{pol:.2f} m²*\n🏠 Devorlar: *{devor:.2f} m²*\n🔝 Shift: *{shift:.2f} m²*\n✅ Jami yuza: *{jami:.2f} m²*"
def calc_uchburchak(a, b, c):
    s = (a+b+c)/2
    maydon = math.sqrt(s*(s-a)*(s-b)*(s-c))
    return f"🔺 *Uch burchak:*\nTomonlar: {a}m, {b}m, {c}m\n✅ Maydon: *{maydon:.2f} m²*\n✅ Perimetr: *{a+b+c:.2f} m*"
def calc_doira(r): return f"⭕ *Doira:*\nRadius: {r}m\n✅ Maydon: *{math.pi*r*r:.2f} m²*\n✅ Aylana: *{2*math.pi*r:.2f} m*"

# =====================
# BUYRUQLAR
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Yaratuvchi Bot* ga xush kelibsiz!\n\nXizmatni tanlang:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "menu":
        await query.message.reply_text("🏠 *Bosh menyu:*", reply_markup=main_menu_keyboard(), parse_mode="Markdown")

    elif data == "havo":
        user_states[user_id] = "waiting_city"
        await query.message.reply_text("📍 Shahar nomini yozing:", reply_markup=back_to_menu())

    elif data == "kurs":
        await query.message.reply_text(get_currency(), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu"), InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]]))

    elif data == "admin":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
        ])
        await query.message.reply_text("👨‍💼 *Admin:*", reply_markup=kb, parse_mode="Markdown")

    elif data == "qurilish":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📐 Maydon", callback_data="c_maydon"),
             InlineKeyboardButton("🏠 Uy yuzasi", callback_data="c_yuza")],
            [InlineKeyboardButton("🧱 G'isht", callback_data="c_gisht"),
             InlineKeyboardButton("🎨 Bo'yoq", callback_data="c_boyoq")],
            [InlineKeyboardButton("🔲 Plitka", callback_data="c_plitka"),
             InlineKeyboardButton("💰 Narx", callback_data="c_narx")],
            [InlineKeyboardButton("🪟 Deraza/Eshik", callback_data="c_deraza"),
             InlineKeyboardButton("🏗 Sement", callback_data="c_sement")],
            [InlineKeyboardButton("🔩 Temir-beton", callback_data="c_temir")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("🏠 *Qurilish Kalkulyatori:*", reply_markup=kb, parse_mode="Markdown")

    elif data == "arxitektura":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📏 Perimetr", callback_data="a_perimetr")],
            [InlineKeyboardButton("📐 To'liq yuza", callback_data="a_yuza")],
            [InlineKeyboardButton("🔺 Uch burchak maydon", callback_data="a_uchburchak")],
            [InlineKeyboardButton("⭕ Doira maydon", callback_data="a_doira")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("📐 *Arxitektura Kalkulyatori:*", reply_markup=kb, parse_mode="Markdown")

    # Qurilish
    elif data == "c_maydon":
        user_states[user_id] = "c_maydon_1"; context.user_data["c"] = {}
        await query.message.reply_text("📐 Uzunlikni yozing (m):", reply_markup=back_to_qurilish())
    elif data == "c_yuza":
        user_states[user_id] = "c_yuza_1"; context.user_data["c"] = {}
        await query.message.reply_text("🏠 Uy uzunligini yozing (m):", reply_markup=back_to_qurilish())
    elif data == "c_gisht":
        user_states[user_id] = "c_gisht_1"; context.user_data["c"] = {}
        await query.message.reply_text("🧱 Bino uzunligini yozing (m):", reply_markup=back_to_qurilish())
    elif data == "c_boyoq":
        user_states[user_id] = "c_boyoq_1"
        await query.message.reply_text("🎨 Maydonni yozing (m²):", reply_markup=back_to_qurilish())
    elif data == "c_plitka":
        user_states[user_id] = "c_plitka_1"; context.user_data["c"] = {}
        await query.message.reply_text("🔲 Xona uzunligini yozing (m):", reply_markup=back_to_qurilish())
    elif data == "c_narx":
        user_states[user_id] = "c_narx_1"; context.user_data["c"] = {}
        await query.message.reply_text("💰 Maydonni yozing (m²):", reply_markup=back_to_qurilish())
    elif data == "c_deraza":
        user_states[user_id] = "c_deraza_1"; context.user_data["c"] = {}
        await query.message.reply_text("🪟 Bino uzunligini yozing (m):", reply_markup=back_to_qurilish())
    elif data == "c_sement":
        user_states[user_id] = "c_sement_1"
        await query.message.reply_text("🏗 Qurilish maydonini yozing (m²):", reply_markup=back_to_qurilish())
    elif data == "c_temir":
        user_states[user_id] = "c_temir_1"; context.user_data["c"] = {}
        await query.message.reply_text("🔩 Poydevor uzunligini yozing (m):", reply_markup=back_to_qurilish())

    # Arxitektura
    elif data == "a_perimetr":
        user_states[user_id] = "a_perimetr_1"; context.user_data["c"] = {}
        await query.message.reply_text("📏 Uzunlikni yozing (m):", reply_markup=back_to_arxitektura())
    elif data == "a_yuza":
        user_states[user_id] = "a_yuza_1"; context.user_data["c"] = {}
        await query.message.reply_text("📐 Uzunlikni yozing (m):", reply_markup=back_to_arxitektura())
    elif data == "a_uchburchak":
        user_states[user_id] = "a_uch_1"; context.user_data["c"] = {}
        await query.message.reply_text("🔺 Birinchi tomonni yozing (m):", reply_markup=back_to_arxitektura())
    elif data == "a_doira":
        user_states[user_id] = "a_doira_1"
        await query.message.reply_text("⭕ Radiusni yozing (m):", reply_markup=back_to_arxitektura())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = user_states.get(user_id, "")
    c = context.user_data.get("c", {})

    try:
        val = float(text)

        if state == "waiting_city":
            await update.message.reply_text(get_weather(text), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu"), InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]]))
            user_states.pop(user_id, None)

        # Maydon
        elif state == "c_maydon_1":
            c["u"] = val; user_states[user_id] = "c_maydon_2"
            await update.message.reply_text("📐 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_maydon_2":
            await update.message.reply_text(calc_maydon(c["u"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Yuza
        elif state == "c_yuza_1":
            c["u"] = val; user_states[user_id] = "c_yuza_2"
            await update.message.reply_text("🏠 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_yuza_2":
            c["k"] = val; user_states[user_id] = "c_yuza_3"
            await update.message.reply_text("🏠 Balandlikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_yuza_3":
            await update.message.reply_text(calc_yuza_q(c["u"], c["k"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # G'isht
        elif state == "c_gisht_1":
            c["u"] = val; user_states[user_id] = "c_gisht_2"
            await update.message.reply_text("🧱 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_gisht_2":
            c["k"] = val; user_states[user_id] = "c_gisht_3"
            await update.message.reply_text("🧱 Balandlikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_gisht_3":
            await update.message.reply_text(calc_gisht(c["u"], c["k"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Bo'yoq
        elif state == "c_boyoq_1":
            await update.message.reply_text(calc_boyoq(val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Plitka
        elif state == "c_plitka_1":
            c["u"] = val; user_states[user_id] = "c_plitka_2"
            await update.message.reply_text("🔲 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_plitka_2":
            c["k"] = val; user_states[user_id] = "c_plitka_3"
            await update.message.reply_text("🔲 Plitka uzunligini yozing (sm):", reply_markup=back_to_qurilish())
        elif state == "c_plitka_3":
            c["po"] = val; user_states[user_id] = "c_plitka_4"
            await update.message.reply_text("🔲 Plitka kengligini yozing (sm):", reply_markup=back_to_qurilish())
        elif state == "c_plitka_4":
            await update.message.reply_text(calc_plitka(c["u"], c["k"], c["po"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Narx
        elif state == "c_narx_1":
            c["m"] = val; user_states[user_id] = "c_narx_2"
            await update.message.reply_text("💰 1 m² narxini yozing (so'm):", reply_markup=back_to_qurilish())
        elif state == "c_narx_2":
            await update.message.reply_text(calc_narx(c["m"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Deraza
        elif state == "c_deraza_1":
            c["u"] = val; user_states[user_id] = "c_deraza_2"
            await update.message.reply_text("🪟 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_deraza_2":
            c["k"] = val; user_states[user_id] = "c_deraza_3"
            await update.message.reply_text("🪟 Deraza sonini yozing:", reply_markup=back_to_qurilish())
        elif state == "c_deraza_3":
            c["d"] = int(val); user_states[user_id] = "c_deraza_4"
            await update.message.reply_text("🚪 Eshik sonini yozing:", reply_markup=back_to_qurilish())
        elif state == "c_deraza_4":
            await update.message.reply_text(calc_deraza(c["u"], c["k"], c["d"], int(val)), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Sement
        elif state == "c_sement_1":
            await update.message.reply_text(calc_sement(val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Temir-beton
        elif state == "c_temir_1":
            c["u"] = val; user_states[user_id] = "c_temir_2"
            await update.message.reply_text("🔩 Kenglikni yozing (m):", reply_markup=back_to_qurilish())
        elif state == "c_temir_2":
            c["k"] = val; user_states[user_id] = "c_temir_3"
            await update.message.reply_text("🔩 Qalinlikni yozing (m, masalan: 0.3):", reply_markup=back_to_qurilish())
        elif state == "c_temir_3":
            await update.message.reply_text(calc_temir(c["u"], c["k"], val), parse_mode="Markdown", reply_markup=done_qurilish())
            user_states.pop(user_id, None)

        # Perimetr
        elif state == "a_perimetr_1":
            c["u"] = val; user_states[user_id] = "a_perimetr_2"
            await update.message.reply_text("📏 Kenglikni yozing (m):", reply_markup=back_to_arxitektura())
        elif state == "a_perimetr_2":
            await update.message.reply_text(calc_perimetr(c["u"], val), parse_mode="Markdown", reply_markup=done_arxitektura())
            user_states.pop(user_id, None)

        # Yuza (arxitektura)
        elif state == "a_yuza_1":
            c["u"] = val; user_states[user_id] = "a_yuza_2"
            await update.message.reply_text("📐 Kenglikni yozing (m):", reply_markup=back_to_arxitektura())
        elif state == "a_yuza_2":
            c["k"] = val; user_states[user_id] = "a_yuza_3"
            await update.message.reply_text("📐 Balandlikni yozing (m):", reply_markup=back_to_arxitektura())
        elif state == "a_yuza_3":
            await update.message.reply_text(calc_yuza_a(c["u"], c["k"], val), parse_mode="Markdown", reply_markup=done_arxitektura())
            user_states.pop(user_id, None)

        # Uch burchak
        elif state == "a_uch_1":
            c["a"] = val; user_states[user_id] = "a_uch_2"
            await update.message.reply_text("🔺 Ikkinchi tomonni yozing (m):", reply_markup=back_to_arxitektura())
        elif state == "a_uch_2":
            c["b"] = val; user_states[user_id] = "a_uch_3"
            await update.message.reply_text("🔺 Uchinchi tomonni yozing (m):", reply_markup=back_to_arxitektura())
        elif state == "a_uch_3":
            await update.message.reply_text(calc_uchburchak(c["a"], c["b"], val), parse_mode="Markdown", reply_markup=done_arxitektura())
            user_states.pop(user_id, None)

        # Doira
        elif state == "a_doira_1":
            await update.message.reply_text(calc_doira(val), parse_mode="Markdown", reply_markup=done_arxitektura())
            user_states.pop(user_id, None)

        else:
            await update.message.reply_text("Menyu uchun /start yozing! 😊", reply_markup=back_to_menu())

    except ValueError:
        if state == "waiting_city":
            await update.message.reply_text(get_weather(text), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu"), InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]]))
            user_states.pop(user_id, None)
        else:
            await update.message.reply_text("❌ Raqam kiriting! Masalan: 5 yoki 5.5", reply_markup=back_to_menu())

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
