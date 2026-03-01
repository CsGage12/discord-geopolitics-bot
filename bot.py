import discord
import feedparser
import requests
import asyncio
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

RSS_URL = "https://feeds.bbci.co.uk/news/world/rss.xml"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

posted = set()

def ask_ai(text):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Foglalld össze magyarul ezt a geopolitikai hírt.

Add meg:

- Rövid összefoglaló
- Előzmények
- Lehetséges következmények

{text}
"""

    json_data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=json_data
    )

    return response.json()["choices"][0]["message"]["content"]


async def news_loop():

    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while True:

        feed = feedparser.parse(RSS_URL)

        for entry in feed.entries[:3]:

            if entry.link not in posted:

                posted.add(entry.link)

                ai = ask_ai(entry.title + " " + entry.summary)

                msg = f"🌍 **{entry.title}**\n\n{ai}\n\n{entry.link}"

                await channel.send(msg)

        await asyncio.sleep(600)


@client.event
async def on_ready():
    print("Bot running")
    client.loop.create_task(news_loop())

client.run(DISCORD_TOKEN)
