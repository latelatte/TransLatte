import discord
import requests
from langdetect import detect
import os

# 環境変数からトークンを取得
Discord_Token = os.environ['DISCORD_TOKEN']
DeepL_Token = os.environ['DEEPL_API_KEY']

# 動作指定チャンネル
Discord_channel_ID = 1351982674604064852

Intents = discord.Intents.default()
Intents.message_content = True

client = discord.Client(intents=Intents)

# 機能有効状態を管理するフラグ
active = True

# 言語判別関数
def language(text):
    return detect(text)

# 起動時の動作
@client.event
async def on_ready():
    print("起動しました")

# メッセージ受信時の動作
@client.event
async def on_message(message):
    global active

    # 指定チャンネル以外は無視
    if message.channel.id != Discord_channel_ID:
        return
    # Bot自身のメッセージは無視
    if message.author == client.user:
        return

    # 機能停止コマンド（Bot自体は停止しない）
    if message.content.startswith("機能停止"):
        active = False
        await message.channel.send("翻訳機能を停止しました")
        return
    # 機能再開コマンド
    if message.content.startswith("機能再開"):
        active = True
        await message.channel.send("翻訳機能を再開しました")
        return

    # 機能停止中は何もしない
    if not active:
        return

    # 以下、翻訳処理
    source_lang = language(message.content)
    target_lang = "EN" if source_lang == "ja" else "JA"

    params = {
        "auth_key": DeepL_Token,
        "text": message.content,
        "source_lang": source_lang,
        "target_lang": target_lang
    }

    response = requests.post("https://api-free.deepl.com/v2/translate", data=params)

    if response.status_code == 200:
        response_json = response.json()
        translated_text = response_json["translations"][0]["text"]
        await message.channel.send(translated_text)
    else:
        await message.channel.send(f"エラー: {response.status_code}\n{response.text}")

client.run(Discord_Token)
