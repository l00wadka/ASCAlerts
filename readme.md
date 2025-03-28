# Alert Bot

This bot provides notifications for a ASC collection on Rarible.

# Dependences:
API KEY
1. https://api.rarible.org/dashboard/api-keys - visit the link
2. Click on Login & complete registration ![alt text](image.png)
3. Create MAINNET API KEY - Copy it & Paste to config.py![alt text](image-2.png)

Bot Token
1. Head to @BotFather in telegram
2. Hit Start and type /newbot
3. Name the bot and copy his token and paste to config.py ![alt text](image-1.png)
4. Head to your created bot and hit /start

Traits
1. All traits stored in traits.json
2. Input "Value" to config to get filtered notifications
3. EG - if you want to get notifications with Gojo hair and Schooler frog - input "Sato" and "Frog"
4. By default you won't get filtered notifications - every listed will shown up

## Installation

1. Install Python 3.11
2. Clone this repository
3. Install dependencies:
pip install -r requirements.txt
4. Configure `config.py` with your details (API-KEY, BOT TOKEN, USER_ID, traits)

## Running the Bot

Start the bot with: python main.py

