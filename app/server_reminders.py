from telegram.ext import Application, ContextTypes, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import __version__ as TG_VER
import os
from dotenv import load_dotenv
from firebase import Database

from models import User, Context, Message, Step

import log
logger = log.setup_logger("reminders")


try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


load_dotenv()


class RemindersServer:
    def __init__(self, token, db: Database):
        self.db = db
        self.application = Application.builder().token(token).build()

    def run(self):
        rems = self.db.get_expired_reminders()
        for r in rems:
            print(r)
