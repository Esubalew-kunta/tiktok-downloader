# Telegram Social Media Downloader Bot

A simple backend-only Telegram bot that accepts a social media link, downloads the media using `yt-dlp`, and sends the file back to the user in Telegram.

## Features
- No database
- Telegram bot API integration
- Downloads video/audio/image from supported URLs
- Sends the media back to the user via Telegram
- Restricts usage to allowed Telegram user IDs

## Setup
1. Create a bot with BotFather in Telegram.
2. Copy your bot token into `.env`.
3. For a public bot, leave `ALLOWED_USER_IDS` empty. For a private bot, add your Telegram user ID(s) separated by commas.
4. Install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
5. Start the bot:
   ```bash
   .venv\Scripts\python main.py
   ```

## Notes
- This works best with direct media links and supported social URLs.
- Some platforms block downloads or require login/session cookies.
- `yt-dlp` is the download engine and may not support every site.
