import asyncio
import logging
import math
import random
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
# KLAVIATURALAR
# =====================

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏗 Qurilish", callback_data="qurilish"),
         InlineKeyboardButton("📐 Arxitektura", callback_data="arxitektura")],
        [InlineKeyboardButton("📊 Matematika", callback_data="matematika"),
         InlineKeyboardButton("💰 Moliya", callback_data="moliya")],
        [InlineKeyboardButton("🎮 O'yinlar", callback_data="oyinlar")],
        [InlineKeyboardButton("👨‍💼 Admin", callback_data="admin")],
    ])

def back(to): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=to)]])
def done(to): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=to), InlineKeyboardButton("🏠 Bosh menyu", callback_data="menu")]])

# =====================
# HISOBLASH FUNKSIYALARI
# =====================

# --- QURILISH ---
def c_maydon(u,k): return f"📐 *Maydon:*\n{u}m × {k}m = *{u*k:.2f} m²*"
def c_yuza(u,k,b): return f"🏠 *Uy yuzasi:*\n📐 Pol: *{u*k:.2f} m²*\n🏠 Devorlar: *{2*(u+k)*b:.2f} m²*\n🔝 Shift: *{u*k:.2f} m²*\n✅ Jami: *{u*k*2+2*(u+k)*b:.2f} m²*"
def c_gisht(u,k,b):
    d=2*(u+k)*b; g=int(d*51)
    return f"🧱 *G'isht:*\nDevor: {d:.2f} m²\n✅ *{g} dona* (~{g//500+1} pallet)"
def c_boyoq(m): return f"🎨 *Bo'yoq:*\n✅ *{m/10:.1f} litr* (~{int(m/10/4)+1} banka)"
def c_plitka(u,k,po,pk):
    xm=u*k; pm=(po/100)*(pk/100); soni=int(xm/pm*1.1)
    return f"🔲 *Plitka:*\nXona: {xm:.2f} m²\n✅ *{soni} dona* (+10% zaxira)"
def c_narx(m,n):
    j=m*n
    return f"💰 *Narx:*\n✅ *{j:,.0f} so'm* (~${j/12900:.0f})"
def c_deraza(u,k,d,e):
    devor=2*(u+k)*k; sof=devor-d*1.5-e*2.0
    return f"🪟 *Deraza/Eshik:*\nDevor: {devor:.2f} m²\n✅ Sof devor: *{sof:.2f} m²*"
def c_sement(m): return f"🏗 *Sement:*\n✅ *{m*0.3:.1f} qop* | Qum: *{m:.1f} m³* | Shag'al: *{m*1.2:.1f} m³*"
def c_temir(u,k,b):
    h=u*k*b
    return f"🔩 *Temir-beton:*\nHajm: {h:.2f} m³\n✅ Temir: *{h*100:.0f} kg* | Beton: *{h*1.5:.2f} m³*"
def c_beton(u,k,b):
    u_m=u/100; k_m=k/100; b_m=b/100; h=u_m*k_m*b_m
    return f"📦 *Beton kubi:*\n{u}sm × {k}sm × {b}sm\n✅ Hajm: *{h:.4f} m³* (~{h*1000:.2f} litr)"
def c_yogoch(u,k,q):
    m=u*k; s=math.ceil(m/(k*q/100))
    return f"🪵 *Yog'och:*\n{m:.2f} m² uchun\n✅ *{s} dona* (qalinlik: {q}sm)"
def c_tom(u,k,n):
    rad=math.radians(n); tl=k/(2*math.cos(rad)); tm=u*tl*2
    return f"🏔 *Tom:*\nNishablik: {n}°\n✅ Uzunlik: *{tl:.2f} m* | Maydon: *{tm:.2f} m²*"
def c_suvoq(u,k,b,q):
    d=2*(u+k)*b; s=d*q/10
    return f"🪣 *Suvoq:*\nDevor: {d:.2f} m²\n✅ *{s:.1f} kg* suvoq (qalinlik: {q}mm)"
def c_zina(h,pog):
    bir=h/pog; chuq=bir*1.5
    return f"🪜 *Zina:*\nUmumiy: {h}m | Pog'ona: {pog} ta\n✅ Har pog'ona: *{bir:.2f}m* baland, *{chuq:.2f}m* chuqur"

# --- ARXITEKTURA ---
def a_perimetr(u,k): return f"📏 *Perimetr:*\n✅ P = 2×({u}+{k}) = *{2*(u+k):.2f} m*"
def a_yuza(u,k,b):
    pol=u*k; devor=2*(u+k)*b; shift=u*k
    return f"📐 *To'liq yuza:*\n📐 Pol: *{pol:.2f} m²*\n🏠 Devorlar: *{devor:.2f} m²*\n🔝 Shift: *{shift:.2f} m²*\n✅ Jami: *{pol+devor+shift:.2f} m²*"
def a_uchburchak(a,b,c):
    s=(a+b+c)/2; m=math.sqrt(s*(s-a)*(s-b)*(s-c))
    return f"🔺 *Uch burchak:*\n✅ Maydon: *{m:.2f} m²* | Perimetr: *{a+b+c:.2f} m*"
def a_doira(r): return f"⭕ *Doira:*\n✅ Maydon: *{math.pi*r*r:.2f} m²* | Aylana: *{2*math.pi*r:.2f} m*"
def a_trapetsiya(a,b,h): return f"📐 *Trapetsiya:*\n✅ Maydon: *{(a+b)/2*h:.2f} m²*"
def a_kvadrat(n): return f"🔢 *Natija:*\n{n}² = *{n**2:.4f}*"
def a_kub(n): return f"📦 *Natija:*\n{n}³ = *{n**3:.4f}*"

# --- MATEMATIKA ---
def m_kvadrat(n): return f"🔢 *Kvadrat:*\n{n}² = *{n*n:.6f}*"
def m_kub(n): return f"📦 *Kub:*\n{n}³ = *{n*n*n:.6f}*"
def m_ortacha(nums):
    o=sum(nums)/len(nums)
    return f"📊 *O'rtacha:*\nSonlar: {', '.join(map(str,nums))}\n✅ O'rtacha: *{o:.4f}*"
def m_daraja(a,b): return f"🔄 *Daraja:*\n{a}^{b} = *{a**b:.6f}*"

# --- MOLIYA ---
def f_kredit(s,f,y):
    r=f/100/12; n=y*12
    if r==0: oylik=s/n
    else: oylik=s*r*(1+r)**n/((1+r)**n-1)
    jami=oylik*n
    return f"🏦 *Kredit:*\nSumma: {s:,} so'm | Foiz: {f}% | Muddat: {y} yil\n✅ Oylik: *{oylik:,.0f} so'm*\n✅ Jami: *{jami:,.0f} so'm*"
def f_foiz(s,f): return f"📈 *Foiz:*\n{s:,} so'mning {f}%\n✅ *{s*f/100:,.0f} so'm*\n✅ Jami: *{s+s*f/100:,.0f} so'm*"
def f_valyuta(s,t):
    kurslar={"USD":12900,"EUR":14100,"RUB":143}
    if t.upper() in kurslar:
        k=kurslar[t.upper()]
        return f"💵 *Valyuta:*\n{s} {t.upper()} = *{s*k:,.0f} so'm*\n(Kurs: 1 {t.upper()} = {k:,} so'm)"
    return "❌ Faqat USD, EUR, RUB"

# =====================
# BUYRUQLAR
# =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Yaratuvchi Bot* ga xush kelibsiz!\n\nXizmatni tanlang:",
        reply_markup=main_menu(), parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    d = query.data

    if d == "menu":
        await query.message.reply_text("🏠 *Bosh menyu:*", reply_markup=main_menu(), parse_mode="Markdown")

    elif d == "admin":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Admin", url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
        ])
        await query.message.reply_text("👨‍💼 *Admin:*", reply_markup=kb, parse_mode="Markdown")

    elif d == "qurilish":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📐 Maydon", callback_data="c_maydon"), InlineKeyboardButton("🏠 Uy yuzasi", callback_data="c_yuza")],
            [InlineKeyboardButton("🧱 G'isht", callback_data="c_gisht"), InlineKeyboardButton("🎨 Bo'yoq", callback_data="c_boyoq")],
            [InlineKeyboardButton("🔲 Plitka", callback_data="c_plitka"), InlineKeyboardButton("💰 Narx", callback_data="c_narx")],
            [InlineKeyboardButton("🪟 Deraza/Eshik", callback_data="c_deraza"), InlineKeyboardButton("🏗 Sement", callback_data="c_sement")],
            [InlineKeyboardButton("🔩 Temir-beton", callback_data="c_temir"), InlineKeyboardButton("📦 Beton kubi", callback_data="c_beton")],
            [InlineKeyboardButton("🪵 Yog'och", callback_data="c_yogoch"), InlineKeyboardButton("🏔 Tom", callback_data="c_tom")],
            [InlineKeyboardButton("🪣 Suvoq", callback_data="c_suvoq"), InlineKeyboardButton("🪜 Zina", callback_data="c_zina")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("🏗 *Qurilish Kalkulyatori:*", reply_markup=kb, parse_mode="Markdown")

    elif d == "arxitektura":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📏 Perimetr", callback_data="a_perimetr"), InlineKeyboardButton("📐 To'liq yuza", callback_data="a_yuza")],
            [InlineKeyboardButton("🔺 Uch burchak", callback_data="a_uchburchak"), InlineKeyboardButton("⭕ Doira", callback_data="a_doira")],
            [InlineKeyboardButton("📐 Trapetsiya", callback_data="a_trapetsiya")],
            [InlineKeyboardButton("🔢 Kvadrat (n²)", callback_data="a_kvadrat"), InlineKeyboardButton("📦 Kub (n³)", callback_data="a_kub")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("📐 *Arxitektura Kalkulyatori:*", reply_markup=kb, parse_mode="Markdown")

    elif d == "matematika":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔢 Kvadrat (n²)", callback_data="m_kvadrat"), InlineKeyboardButton("📦 Kub (n³)", callback_data="m_kub")],
            [InlineKeyboardButton("📊 O'rtacha qiymat", callback_data="m_ortacha")],
            [InlineKeyboardButton("🔄 Daraja (aⁿ)", callback_data="m_daraja")],
            [InlineKeyboardButton("➕ Oddiy kalkulyator", callback_data="m_kalk")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("📊 *Matematika:*", reply_markup=kb, parse_mode="Markdown")

    elif d == "moliya":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏦 Kredit", callback_data="f_kredit")],
            [InlineKeyboardButton("📈 Foiz hisoblash", callback_data="f_foiz")],
            [InlineKeyboardButton("💵 Valyuta", callback_data="f_valyuta")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("💰 *Moliya:*", reply_markup=kb, parse_mode="Markdown")

    elif d == "oyinlar":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🃏 Karta o'yini", callback_data="o_karta")],
            [InlineKeyboardButton("🐍 Ilon o'yini", callback_data="o_ilon")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")],
        ])
        await query.message.reply_text("🎮 *O'yinlar:*", reply_markup=kb, parse_mode="Markdown")

    # --- QURILISH TUGMALARI ---
    elif d == "c_maydon": user_states[uid]="c_maydon_1"; context.user_data["c"]={}; await query.message.reply_text("📐 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_yuza": user_states[uid]="c_yuza_1"; context.user_data["c"]={}; await query.message.reply_text("🏠 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_gisht": user_states[uid]="c_gisht_1"; context.user_data["c"]={}; await query.message.reply_text("🧱 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_boyoq": user_states[uid]="c_boyoq_1"; await query.message.reply_text("🎨 Maydon (m²):", reply_markup=back("qurilish"))
    elif d == "c_plitka": user_states[uid]="c_plitka_1"; context.user_data["c"]={}; await query.message.reply_text("🔲 Xona uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_narx": user_states[uid]="c_narx_1"; context.user_data["c"]={}; await query.message.reply_text("💰 Maydon (m²):", reply_markup=back("qurilish"))
    elif d == "c_deraza": user_states[uid]="c_deraza_1"; context.user_data["c"]={}; await query.message.reply_text("🪟 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_sement": user_states[uid]="c_sement_1"; await query.message.reply_text("🏗 Maydon (m²):", reply_markup=back("qurilish"))
    elif d == "c_temir": user_states[uid]="c_temir_1"; context.user_data["c"]={}; await query.message.reply_text("🔩 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_beton": user_states[uid]="c_beton_1"; context.user_data["c"]={}; await query.message.reply_text("📦 Uzunlik (sm):", reply_markup=back("qurilish"))
    elif d == "c_yogoch": user_states[uid]="c_yogoch_1"; context.user_data["c"]={}; await query.message.reply_text("🪵 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_tom": user_states[uid]="c_tom_1"; context.user_data["c"]={}; await query.message.reply_text("🏔 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_suvoq": user_states[uid]="c_suvoq_1"; context.user_data["c"]={}; await query.message.reply_text("🪣 Uzunlik (m):", reply_markup=back("qurilish"))
    elif d == "c_zina": user_states[uid]="c_zina_1"; context.user_data["c"]={}; await query.message.reply_text("🪜 Umumiy balandlik (m):", reply_markup=back("qurilish"))

    # --- ARXITEKTURA TUGMALARI ---
    elif d == "a_perimetr": user_states[uid]="a_perimetr_1"; context.user_data["c"]={}; await query.message.reply_text("📏 Uzunlik (m):", reply_markup=back("arxitektura"))
    elif d == "a_yuza": user_states[uid]="a_yuza_1"; context.user_data["c"]={}; await query.message.reply_text("📐 Uzunlik (m):", reply_markup=back("arxitektura"))
    elif d == "a_uchburchak": user_states[uid]="a_uch_1"; context.user_data["c"]={}; await query.message.reply_text("🔺 1-tomon (m):", reply_markup=back("arxitektura"))
    elif d == "a_doira": user_states[uid]="a_doira_1"; await query.message.reply_text("⭕ Radius (m):", reply_markup=back("arxitektura"))
    elif d == "a_trapetsiya": user_states[uid]="a_trap_1"; context.user_data["c"]={}; await query.message.reply_text("📐 Yuqori tomon (m):", reply_markup=back("arxitektura"))
    elif d == "a_kvadrat": user_states[uid]="a_kvadrat_1"; await query.message.reply_text("🔢 Sonni yozing:", reply_markup=back("arxitektura"))
    elif d == "a_kub": user_states[uid]="a_kub_1"; await query.message.reply_text("📦 Sonni yozing:", reply_markup=back("arxitektura"))

    # --- MATEMATIKA TUGMALARI ---
    elif d == "m_kvadrat": user_states[uid]="m_kvadrat_1"; await query.message.reply_text("🔢 Sonni yozing:", reply_markup=back("matematika"))
    elif d == "m_kub": user_states[uid]="m_kub_1"; await query.message.reply_text("📦 Sonni yozing:", reply_markup=back("matematika"))
    elif d == "m_ortacha": user_states[uid]="m_ortacha_1"; await query.message.reply_text("📊 Sonlarni vergul bilan yozing:\nMasalan: 10, 20, 30", reply_markup=back("matematika"))
    elif d == "m_daraja": user_states[uid]="m_daraja_1"; context.user_data["c"]={}; await query.message.reply_text("🔄 Asosni yozing (a):", reply_markup=back("matematika"))
    elif d == "m_kalk": user_states[uid]="m_kalk_1"; await query.message.reply_text("➕ Hisob yozing:\nMasalan: 5+3, 10*4, 100/5, 7-2", reply_markup=back("matematika"))

    # --- MOLIYA TUGMALARI ---
    elif d == "f_kredit": user_states[uid]="f_kredit_1"; context.user_data["c"]={}; await query.message.reply_text("🏦 Kredit summasi (so'm):", reply_markup=back("moliya"))
    elif d == "f_foiz": user_states[uid]="f_foiz_1"; context.user_data["c"]={}; await query.message.reply_text("📈 Summa (so'm):", reply_markup=back("moliya"))
    elif d == "f_valyuta": user_states[uid]="f_valyuta_1"; context.user_data["c"]={}; await query.message.reply_text("💵 Summa yozing:", reply_markup=back("moliya"))

    # --- O'YINLAR ---
    elif d == "o_karta":
        karta = random.choice(["♠️ A","♥️ K","♦️ Q","♣️ J","♠️ 10","♥️ 9","♦️ 8","♣️ 7"])
        bot_karta = random.choice(["♠️ A","♥️ K","♦️ Q","♣️ J","♠️ 10","♥️ 9","♦️ 8","♣️ 7"])
        karta_qiymat = {"A":14,"K":13,"Q":12,"J":11,"10":10,"9":9,"8":8,"7":7}
        siz = karta_qiymat[karta.split()[-1]]
        bot = karta_qiymat[bot_karta.split()[-1]]
        natija = "🏆 Siz yutdingiz!" if siz > bot else ("🤝 Durang!" if siz == bot else "🤖 Bot yutdi!")
        await query.message.reply_text(
            f"🃏 *Karta o'yini:*\n\nSiz: *{karta}*\nBot: *{bot_karta}*\n\n{natija}",
            parse_mode="Markdown", reply_markup=done("oyinlar")
        )

    elif d == "o_ilon":
        user_states[uid] = "ilon_game"
        context.user_data["ilon"] = {"son": random.randint(1,100), "urinish": 0}
        await query.message.reply_text(
            "🐍 *Ilon o'yini!*\n\n1 dan 100 gacha son o'yladim.\nToping! (10 ta urinish)",
            parse_mode="Markdown", reply_markup=back("oyinlar")
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    state = user_states.get(uid, "")
    c = context.user_data.get("c", {})

    # ILON O'YINI
    if state == "ilon_game":
        try:
            son = context.user_data["ilon"]["son"]
            urinish = context.user_data["ilon"]["urinish"] + 1
            context.user_data["ilon"]["urinish"] = urinish
            taxmin = int(text)
            if taxmin == son:
                await update.message.reply_text(f"🎉 *To'g'ri!* {son} edi! {urinish} ta urinishda topdingiz!", parse_mode="Markdown", reply_markup=done("oyinlar"))
                user_states.pop(uid, None)
            elif urinish >= 10:
                await update.message.reply_text(f"❌ *10 urinish tugadi!* Son *{son}* edi.", parse_mode="Markdown", reply_markup=done("oyinlar"))
                user_states.pop(uid, None)
            elif taxmin < son:
                await update.message.reply_text(f"⬆️ Kattaroq! ({10-urinish} urinish qoldi)", reply_markup=back("oyinlar"))
            else:
                await update.message.reply_text(f"⬇️ Kichikroq! ({10-urinish} urinish qoldi)", reply_markup=back("oyinlar"))
        except:
            await update.message.reply_text("❌ Raqam kiriting!", reply_markup=back("oyinlar"))
        return

    try:
        val = float(text)

        # QURILISH
        if state == "c_maydon_1": c["u"]=val; user_states[uid]="c_maydon_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_maydon_2": await update.message.reply_text(c_maydon(c["u"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_yuza_1": c["u"]=val; user_states[uid]="c_yuza_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_yuza_2": c["k"]=val; user_states[uid]="c_yuza_3"; await update.message.reply_text("Balandlik (m):", reply_markup=back("qurilish"))
        elif state == "c_yuza_3": await update.message.reply_text(c_yuza(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_gisht_1": c["u"]=val; user_states[uid]="c_gisht_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_gisht_2": c["k"]=val; user_states[uid]="c_gisht_3"; await update.message.reply_text("Balandlik (m):", reply_markup=back("qurilish"))
        elif state == "c_gisht_3": await update.message.reply_text(c_gisht(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_boyoq_1": await update.message.reply_text(c_boyoq(val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_plitka_1": c["u"]=val; user_states[uid]="c_plitka_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_plitka_2": c["k"]=val; user_states[uid]="c_plitka_3"; await update.message.reply_text("Plitka uzunligi (sm):", reply_markup=back("qurilish"))
        elif state == "c_plitka_3": c["po"]=val; user_states[uid]="c_plitka_4"; await update.message.reply_text("Plitka kengligi (sm):", reply_markup=back("qurilish"))
        elif state == "c_plitka_4": await update.message.reply_text(c_plitka(c["u"],c["k"],c["po"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_narx_1": c["m"]=val; user_states[uid]="c_narx_2"; await update.message.reply_text("1 m² narxi (so'm):", reply_markup=back("qurilish"))
        elif state == "c_narx_2": await update.message.reply_text(c_narx(c["m"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_deraza_1": c["u"]=val; user_states[uid]="c_deraza_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_deraza_2": c["k"]=val; user_states[uid]="c_deraza_3"; await update.message.reply_text("Deraza soni:", reply_markup=back("qurilish"))
        elif state == "c_deraza_3": c["d"]=int(val); user_states[uid]="c_deraza_4"; await update.message.reply_text("Eshik soni:", reply_markup=back("qurilish"))
        elif state == "c_deraza_4": await update.message.reply_text(c_deraza(c["u"],c["k"],c["d"],int(val)), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_sement_1": await update.message.reply_text(c_sement(val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_temir_1": c["u"]=val; user_states[uid]="c_temir_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_temir_2": c["k"]=val; user_states[uid]="c_temir_3"; await update.message.reply_text("Qalinlik (m, masalan: 0.3):", reply_markup=back("qurilish"))
        elif state == "c_temir_3": await update.message.reply_text(c_temir(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_beton_1": c["u"]=val; user_states[uid]="c_beton_2"; await update.message.reply_text("En (sm):", reply_markup=back("qurilish"))
        elif state == "c_beton_2": c["k"]=val; user_states[uid]="c_beton_3"; await update.message.reply_text("Balandlik (sm):", reply_markup=back("qurilish"))
        elif state == "c_beton_3": await update.message.reply_text(c_beton(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_yogoch_1": c["u"]=val; user_states[uid]="c_yogoch_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_yogoch_2": c["k"]=val; user_states[uid]="c_yogoch_3"; await update.message.reply_text("Yog'och qalinligi (sm):", reply_markup=back("qurilish"))
        elif state == "c_yogoch_3": await update.message.reply_text(c_yogoch(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_tom_1": c["u"]=val; user_states[uid]="c_tom_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_tom_2": c["k"]=val; user_states[uid]="c_tom_3"; await update.message.reply_text("Nishablik (daraja, masalan: 30):", reply_markup=back("qurilish"))
        elif state == "c_tom_3": await update.message.reply_text(c_tom(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_suvoq_1": c["u"]=val; user_states[uid]="c_suvoq_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("qurilish"))
        elif state == "c_suvoq_2": c["k"]=val; user_states[uid]="c_suvoq_3"; await update.message.reply_text("Balandlik (m):", reply_markup=back("qurilish"))
        elif state == "c_suvoq_3": c["b"]=val; user_states[uid]="c_suvoq_4"; await update.message.reply_text("Suvoq qalinligi (mm, masalan: 15):", reply_markup=back("qurilish"))
        elif state == "c_suvoq_4": await update.message.reply_text(c_suvoq(c["u"],c["k"],c["b"],val), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        elif state == "c_zina_1": c["h"]=val; user_states[uid]="c_zina_2"; await update.message.reply_text("Pog'ona soni:", reply_markup=back("qurilish"))
        elif state == "c_zina_2": await update.message.reply_text(c_zina(c["h"],int(val)), parse_mode="Markdown", reply_markup=done("qurilish")); user_states.pop(uid,None)

        # ARXITEKTURA
        elif state == "a_perimetr_1": c["u"]=val; user_states[uid]="a_perimetr_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("arxitektura"))
        elif state == "a_perimetr_2": await update.message.reply_text(a_perimetr(c["u"],val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        elif state == "a_yuza_1": c["u"]=val; user_states[uid]="a_yuza_2"; await update.message.reply_text("Kenglik (m):", reply_markup=back("arxitektura"))
        elif state == "a_yuza_2": c["k"]=val; user_states[uid]="a_yuza_3"; await update.message.reply_text("Balandlik (m):", reply_markup=back("arxitektura"))
        elif state == "a_yuza_3": await update.message.reply_text(a_yuza(c["u"],c["k"],val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        elif state == "a_uch_1": c["a"]=val; user_states[uid]="a_uch_2"; await update.message.reply_text("2-tomon (m):", reply_markup=back("arxitektura"))
        elif state == "a_uch_2": c["b"]=val; user_states[uid]="a_uch_3"; await update.message.reply_text("3-tomon (m):", reply_markup=back("arxitektura"))
        elif state == "a_uch_3": await update.message.reply_text(a_uchburchak(c["a"],c["b"],val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        elif state == "a_doira_1": await update.message.reply_text(a_doira(val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        elif state == "a_trap_1": c["a"]=val; user_states[uid]="a_trap_2"; await update.message.reply_text("Quyi tomon (m):", reply_markup=back("arxitektura"))
        elif state == "a_trap_2": c["b"]=val; user_states[uid]="a_trap_3"; await update.message.reply_text("Balandlik (m):", reply_markup=back("arxitektura"))
        elif state == "a_trap_3": await update.message.reply_text(a_trapetsiya(c["a"],c["b"],val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        elif state == "a_kvadrat_1": await update.message.reply_text(a_kvadrat(val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)
        elif state == "a_kub_1": await update.message.reply_text(a_kub(val), parse_mode="Markdown", reply_markup=done("arxitektura")); user_states.pop(uid,None)

        # MATEMATIKA
        elif state == "m_kvadrat_1": await update.message.reply_text(m_kvadrat(val), parse_mode="Markdown", reply_markup=done("matematika")); user_states.pop(uid,None)
        elif state == "m_kub_1": await update.message.reply_text(m_kub(val), parse_mode="Markdown", reply_markup=done("matematika")); user_states.pop(uid,None)
        elif state == "m_daraja_1": c["a"]=val; user_states[uid]="m_daraja_2"; await update.message.reply_text("Darajani yozing (n):", reply_markup=back("matematika"))
        elif state == "m_daraja_2": await update.message.reply_text(m_daraja(c["a"],val), parse_mode="Markdown", reply_markup=done("matematika")); user_states.pop(uid,None)

        # MOLIYA
        elif state == "f_kredit_1": c["s"]=val; user_states[uid]="f_kredit_2"; await update.message.reply_text("Yillik foiz (%):", reply_markup=back("moliya"))
        elif state == "f_kredit_2": c["f"]=val; user_states[uid]="f_kredit_3"; await update.message.reply_text("Muddat (yil):", reply_markup=back("moliya"))
        elif state == "f_kredit_3": await update.message.reply_text(f_kredit(c["s"],c["f"],int(val)), parse_mode="Markdown", reply_markup=done("moliya")); user_states.pop(uid,None)

        elif state == "f_foiz_1": c["s"]=val; user_states[uid]="f_foiz_2"; await update.message.reply_text("Foiz (%):", reply_markup=back("moliya"))
        elif state == "f_foiz_2": await update.message.reply_text(f_foiz(c["s"],val), parse_mode="Markdown", reply_markup=done("moliya")); user_states.pop(uid,None)

        elif state == "f_valyuta_1": c["s"]=val; user_states[uid]="f_valyuta_2"; await update.message.reply_text("Valyuta turi (USD, EUR, RUB):", reply_markup=back("moliya"))

        else:
            await update.message.reply_text("Menyu uchun /start yozing! 😊", reply_markup=back("menu"))

    except ValueError:
        # Matn qabul qiluvchi holatlar
        if state == "m_ortacha_1":
            try:
                nums = [float(x.strip()) for x in text.split(",")]
                await update.message.reply_text(m_ortacha(nums), parse_mode="Markdown", reply_markup=done("matematika"))
                user_states.pop(uid,None)
            except:
                await update.message.reply_text("❌ Sonlarni vergul bilan yozing: 10, 20, 30", reply_markup=back("matematika"))

        elif state == "m_kalk_1":
            try:
                allowed = set("0123456789+-*/.() ")
                if all(ch in allowed for ch in text):
                    result = eval(text)
                    await update.message.reply_text(f"➕ *Natija:*\n{text} = *{result}*", parse_mode="Markdown", reply_markup=done("matematika"))
                    user_states.pop(uid,None)
                else:
                    await update.message.reply_text("❌ Faqat raqam va amallar: +, -, *, /", reply_markup=back("matematika"))
            except:
                await update.message.reply_text("❌ Noto'g'ri format. Masalan: 5+3", reply_markup=back("matematika"))

        elif state == "f_valyuta_2":
            await update.message.reply_text(f_valyuta(c["s"],text), parse_mode="Markdown", reply_markup=done("moliya"))
            user_states.pop(uid,None)

        else:
            await update.message.reply_text("❌ Raqam kiriting!", reply_markup=back("menu"))

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
