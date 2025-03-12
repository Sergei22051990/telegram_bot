# Telegram Lottery Bot

A simple Telegram bot that runs a lottery game where users can participate and win prizes.

## Setup

1. Create a `.env` file in the root directory with your bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python bot.py
```

## Features

- `/start` - Start the bot and get information
- `/join_lottery` - Join the current lottery round
- `/draw` - Draw a winner (admin only)
- `/stats` - Check your lottery statistics

## How to Play

1. Start the bot using `/start`
2. Join the lottery using `/join_lottery`
3. Wait for the admin to draw the winner using `/draw`
4. Winners will be announced in the chat 