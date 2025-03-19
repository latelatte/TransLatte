import discord
from discord.ext import commands
import requests
from langdetect import detect
import os


DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DEEPL_TOKEN = os.environ['DEEPL_API_KEY']


intents = discord.Intents.default()
intents.message_content = True

# スラッシュコマンドを使うから多分要らない
bot = commands.Bot(command_prefix="!", intents=intents)

# 機能オンオフのフラグ
active = True

def language(text):
    return detect(text)

@bot.event
async def on_ready():
    print(f"{bot.user} がオンラインになりました")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print("コマンド同期エラー:", e)

# 翻訳機能停止
@bot.tree.command(name="end_translation", description="翻訳機能を停止します")
async def stop_translation(interaction: discord.Interaction):
    global active
    active = False
    await interaction.response.send_message("翻訳機能を停止しましたd(˙꒳​˙* )", ephemeral=False)

# 翻訳機能再開
@bot.tree.command(name="start_translation", description="翻訳機能を開始します")
async def start_translation(interaction: discord.Interaction):
    global active
    active = True
    await interaction.response.send_message("翻訳機能を開始しましたd(˙꒳​˙* )", ephemeral=False)

@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author.bot:
        return

    if not active:
        return

    source_lang = language(message.content)
    target_lang = "EN" if source_lang == "ja" else "JA"
    params = {
        "auth_key": DEEPL_TOKEN,
        "text": message.content,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    response = requests.post("https://api-free.deepl.com/v2/translate", data=params)
    if response.status_code == 200:
        translated_text = response.json()["translations"][0]["text"]
        await message.channel.send(translated_text)
    else:
        await message.channel.send(f"エラー: {response.status_code}\n{response.text}")

    # 再呼び出し
    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
