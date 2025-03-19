import discord
import requests
from langdetect import detect
import os

# 環境変数からトークンを取得
Discord_Token = os.environ['DISCORD_TOKEN']
DeepL_Token = os.environ['DEEPL_TOKEN']  # DeepL のトークンも環境変数で管理する

# 動作指定チャンネル
Discord_channel_ID = 1351982674604064852

intents = discord.Intents.default()
intents.message_content = True

# discord.Client を使い、app_commands でスラッシュコマンドを登録
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# 機能有効状態を管理するフラグ
active = True

# 言語判別関数
def language(text):
    return detect(text)

@client.event
async def on_ready():
    print("起動しました")
    # スラッシュコマンドを同期する
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# 「機能停止」スラッシュコマンド
@tree.command(name="endtrans", description="翻訳機能を停止します")
async def stop_translation(interaction: discord.Interaction):
    global active
    active = False
    await interaction.response.send_message("翻訳を終わります！d(˙꒳​˙* )", ephemeral=True)

# 「機能再開」スラッシュコマンド
@tree.command(name="starttrans", description="翻訳機能を再開します")
async def start_translation(interaction: discord.Interaction):
    global active
    active = True
    await interaction.response.send_message("翻訳を始めます！d(˙꒳​˙* )", ephemeral=True)

# 通常のメッセージイベント（翻訳機能）
@client.event
async def on_message(message):
    # 指定チャンネル以外は無視
    if message.channel.id != Discord_channel_ID:
        return
    # Bot 自身のメッセージは無視
    if message.author == client.user:
        return
    # 機能停止中は何もしない
    if not active:
        return

    # 翻訳処理
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
