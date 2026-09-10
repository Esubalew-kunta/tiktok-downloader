import asyncio
import logging
import os
import threading
from typing import Any

from flask import Flask, jsonify
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .config import ALLOWED_USER_IDS, BOT_TOKEN
from .downloader import DownloadError, download_media

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app_server = Flask(__name__)


@app_server.route("/health", methods=["GET"])
def health_check() -> tuple[str, int]:
    return jsonify({"status": "ok"}), 200


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("You are not allowed to use this bot.")
        return

    await update.message.reply_text(
        "Send me a link to a video or post, and I will try to download and send it back to you."
    )


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("You are not allowed to use this bot.")
        return

    msg = update.message
    if not msg or not msg.text:
        await msg.reply_text("Please send a valid URL.")
        return

    url = msg.text.strip()
    if not url.startswith(("http://", "https://")):
        await msg.reply_text("Please send a valid link starting with http:// or https://")
        return

    await msg.reply_text("Downloading... This may take a few seconds.")

    try:
        file_path, mime_type = download_media(url)
        file_name = os.path.basename(file_path)

        if mime_type.startswith("video/") or mime_type.startswith("audio/"):
            await msg.reply_document(document=open(file_path, "rb"), filename=file_name, caption="Here is your media.")
        elif mime_type.startswith("image/"):
            await msg.reply_photo(photo=open(file_path, "rb"), caption="Here is your image.")
        else:
            await msg.reply_document(document=open(file_path, "rb"), filename=file_name, caption="Here is your downloaded file.")

    except DownloadError as exc:
        await msg.reply_text(f"I could not download that link: {exc}")
    except Exception as exc:
        logger.exception("Unexpected error while processing link")
        await msg.reply_text("Something went wrong while downloading the media. Please try another link.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Use /start to begin. Send a direct URL to a social media post or video and I will try to send it back."
    )


def main() -> None:
    port = int(os.environ.get("PORT", "10000"))

    def run_health_server() -> None:
        app_server.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
