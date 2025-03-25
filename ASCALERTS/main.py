import asyncio
import sys
from aiogram import Bot, Dispatcher
import requests
from asyncio import run, sleep, set_event_loop_policy
import json
from loguru import logger
from aiogram.exceptions import TelegramNetworkError
from config import BOT_TOKEN, API_KEY, OWNER_ID, SLEEP_TIME

if sys.platform == 'win32':
    set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
latest_activity_id = None

def get_rarity(rank):
    try:
        rank = int(rank)
    except ValueError:
        return "Unknown"

    if 1 <= rank <= 33:
        return "💀 Ascended"
    elif 34 <= rank <= 172:
        return "🔥 Mythic"
    elif 173 <= rank <= 507:
        return "🟠 Legendary"
    elif 508 <= rank <= 1500:
        return "🟣 Epic"
    elif 1501 <= rank <= 3500:
        return "🔵 Rare"
    elif 3501 <= rank <= 6000:
        return "🟢 Uncommon"
    elif 6001 <= rank <= 10000:
        return "⚪️ Common"
    return "Unknown"


def load_nft_data():
    logger.info("Loading NFT data from local JSON file...")
    try:
        with open("traits.json", "r", encoding="utf-8") as file:
            nft_data = json.load(file)
            logger.info("NFT data loaded successfully.")
            return nft_data
    except FileNotFoundError:
        logger.error("traits.json file not found.")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file: {e}")
    return []


def format_activity(activity, nft_data):
    base_account_url = "https://eclipsescan.xyz/account/"
    base_item_url = "https://scopenft.xyz/token/"

    activity_type = activity.get('@type', '')
    item_id = activity.get('make', {}).get('type', {}).get('itemId', 'Unknown')
    price = activity.get('price', 'Unknown')
    date = activity.get('date', 'Unknown')
    maker = activity.get('maker', 'Unknown').replace('SOLANA:', '')

    nft_meta = next((nft for nft in nft_data if nft['meta']['id'] == item_id), None)

    if nft_meta:
        rank = nft_meta.get('rank', 'Unknown')
        rarity = get_rarity(rank)
    else:
        rank = "Unknown"
        rarity = "Unknown"

    return (
        f"⚠️ New ASC Listing ⚠️\n"
        f"📅 {date}\n"
        f"🔗 - <a href='{base_item_url}{item_id}'>Scope</a>\n"
        f"💵 Price: {price} ETH\n"
        f"💁🏻 Maker: <a href='{base_account_url}{maker}'>Link</a>\n"
        f"🏆 Rank: {rank}\n"
        f"👀 Rarity: {rarity}\n"
    )


async def fetch_activity():
    url = "https://api.rarible.org/v0.1/activities/byCollection?type=LIST&collection=ECLIPSE%3A6ffVbxEZVWtksbXtQbt8xzudyain8MdsVdkkXxvaxznC"
    headers = {"accept": "application/json", "X-API-KEY": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['activities'][0]
    except Exception as e:
        logger.error(f"Error fetching activity: {e}")
    return None


async def parse_collection():
    global latest_activity_id
    nft_data = load_nft_data()
    while True:
        activity = await fetch_activity()
        if activity and activity['id'] != latest_activity_id:
            latest_activity_id = activity['id']
            formatted_message = format_activity(activity, nft_data)
            logger.info("New activity detected, sending notifications.")
            await bot.send_message(OWNER_ID, formatted_message, parse_mode="HTML")
        else:
            logger.info("No new activity detected.")
        await sleep(SLEEP_TIME)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is starting...")
    asyncio.create_task(parse_collection())
    try:
        await dp.start_polling(bot)
    except TelegramNetworkError as e:
        logger.error(f"Network error: {e}")


if __name__ == '__main__':
    run(main())
