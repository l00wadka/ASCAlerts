import asyncio
import sys
from aiogram import Bot, Dispatcher
import requests
from asyncio import run, sleep, set_event_loop_policy
import json
from loguru import logger
from aiogram.exceptions import TelegramNetworkError
from config import BOT_TOKEN, API_KEY, OWNER_ID, SLEEP_TIME, USER_TRAITS

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
        logger.error(f"Error decoding traits.json file: {e}")
    return []


def check_matching_traits(nft_meta, user_id):
    selected_traits = USER_TRAITS.get(user_id, [])
    if not selected_traits:
        return True

    nft_traits = [attribute['value'] for attribute in nft_meta.get('meta', {}).get('attributes', [])]

    logger.info(f"Checking NFT traits: {nft_traits} against user selected traits: {selected_traits}")

    for trait in selected_traits:
        if trait in nft_traits:
            return True
    return False


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

        if check_matching_traits(nft_meta['meta'], OWNER_ID):
            return (
                f"⚠️ New ASC Listing ⚠️\n"
                f"📅 {date}\n"
                f"🔗 - <a href='{base_item_url}{item_id}'>Scope</a>\n"
                f"💵 Price: {price} ETH\n"
                f"💁🏻 Maker: <a href='{base_account_url}{maker}'>Link</a>\n"
                f"🏆 Rank: {rank}\n"
                f"👀 Rarity: {rarity}\n"
            )
    return None


async def fetch_activity():
    url = "https://api.rarible.org/v0.1/activities/byCollection?type=LIST&collection=ECLIPSE%3A6ffVbxEZVWtksbXtQbt8xzudyain8MdsVdkkXxvaxznC"
    headers = {"accept": "application/json", "X-API-KEY": API_KEY}
    try:
        logger.info("Fetching activity from the server...")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logger.info("Activity fetched successfully.")
            return response.json()['activities'][0]
        else:
            logger.error(f"Error fetching activity: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching activity: {e}")
    return None


async def parse_collection():
    global latest_activity_id
    nft_data = load_nft_data()

    while True:
        logger.info("Checking for new activities...")
        activity = await fetch_activity()
        if activity and activity['id'] != latest_activity_id:
            latest_activity_id = activity['id']
            item_id = activity.get('make', {}).get('type', {}).get('itemId', 'Unknown')

            logger.info(f"New activity detected for NFT {item_id}")
            formatted_message = format_activity(activity, nft_data)
            if formatted_message:
                await bot.send_message(OWNER_ID, formatted_message, parse_mode="HTML")
                logger.info(f"Notification sent for NFT {item_id}")
            else:
                logger.info(f"NFT {item_id} does not match the selected traits.")

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
