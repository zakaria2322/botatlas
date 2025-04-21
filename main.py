import os
import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_seen_token = None


async def fetch_new_token():
    global last_seen_token
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            response = requests.get("https://doggy.market/drc-20")
            soup = BeautifulSoup(response.text, "html.parser")

            tokens = soup.select("a[href^='/token/']")
            if tokens:
                latest_token = tokens[0].get("href").split("/")[-1]

                if latest_token != last_seen_token:
                    last_seen_token = latest_token

                    channel = discord.utils.get(bot.get_all_channels(),
                                                name=CHANNEL_NAME)
                    if channel:
                        await channel.send(
                            f"🚀 عملة جديدة ظهرت على DRC-20!\n"
                            f"📛 الرمز: {latest_token}\n"
                            f"🌐 https://doggy.market/token/{latest_token}")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء قراءة الموقع: {e}")

        await asyncio.sleep(60)  # كل دقيقة


@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {bot.user}")
    channel = discord.utils.get(bot.get_all_channels(), name=CHANNEL_NAME)
    if channel:
        await channel.send("✅ البوت متصل الآن ويعمل بشكل جيد!")
    else:
        print("❌ لم أتمكن من العثور على القناة.")
    bot.loop.create_task(fetch_new_token())


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 البوت شغّال تمام!")


@bot.command()
async def start(ctx):
    await ctx.send("🚀 تم تشغيل نظام المراقبة للعملات!")


@bot.command()
async def info(ctx):
    await ctx.send(
        "🤖 أنا بوت مراقبة العملات الجديدة على موقع doggy.market!\nتابعني وراح أخبرك بأحدث العملات أول بأول 🔥"
    )


@bot.command()
async def helpme(ctx):
    help_text = """
🧾 **أوامر البوت المتوفرة:**
• `!ping` — تأكد إن البوت شغّال
• `!start` — تشغيل نظام المراقبة
• `!info` — معلومات عن البوت
• `!helpme` — عرض هذه الرسالة
• `!check` — فحص العملات الجديدة الآن
• `testnewtoken` — اختبار رسالة عملة جديدة
"""
    await ctx.send(help_text)


@bot.command()
async def testnewtoken(ctx):
    await ctx.send("🚀 عملة جديدة ظهرت على DRC-20!\n"
                   "📛 الرمز: TEST123\n"
                   "🌐 https://doggy.market/token/TEST123")


@bot.command()
async def check(ctx):
    await ctx.send("🔍 جاري فحص العملات الجديدة على doggy.market ...")
    try:
        url = "https://doggy.market/drc-20"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        first_token = soup.select_one("table tbody tr")
        if first_token:
            cols = first_token.find_all("td")
            token_name = cols[0].text.strip()
            mint_info = cols[1].text.strip()
            total_supply = cols[2].text.strip()

            await ctx.send(
                f"🆕 تم العثور على عملة جديدة:\n🔸 الإسم: `{token_name}`\n🔢 Mint: `{mint_info}`\n📦 الكمية: `{total_supply}`"
            )
        else:
            await ctx.send("❌ لم يتم العثور على أي عملة حالياً.")
    except Exception as e:
        await ctx.send("⚠️ حدث خطأ أثناء جلب البيانات.")
        print(f"[Error] {e}")


keep_alive()
bot.run(TOKEN)
