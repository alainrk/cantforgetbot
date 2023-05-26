from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update, Bot
from telegram import __version__ as TG_VER
import os
import hashlib
import datetime
from dotenv import load_dotenv
from firebase import Database

import log
logger = log.setup_logger("bot")


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


def is_user_allowed(user) -> bool:
    return user.username in os.getenv("USERS_ALLOWED").split(",")


async def auth_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # TODO: Temp solution, check if user is allowed to use the bot
    if not is_user_allowed(update.effective_user):
        await update.message.reply_text("You are not allowed to use this bot")
        return False
    return True


async def is_command(text: str) -> bool:
    return text.startswith("/") and len(text.split()) == 1


class Bot:
    def __init__(self, token, db: Database):
        self.db = db
        self.application = Application.builder().token(token).build()
        self.__set_handlers()

    def __set_handlers(self):
        # Single handler for everything, internal FSM will be used to handle the flow
        self.application.add_handler(
            MessageHandler(filters.ALL, self.__process_message))

    def run(self):
        self.application.run_polling()

    async def __process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not (await auth_guard(update, context)):
            return

        dbUser = self.db.get_user(update.effective_user.username)

        if not dbUser.exists:
            dbUser = self.db.add_user(update.effective_user.username, update.effective_user.id,
                                      update.effective_user.first_name, update.effective_user.last_name)

        user = dbUser.to_dict()
        user["context"]["last_message"] = update.message.text
        self.db.update_user_context(user["username"], user["context"])

        # XXX: Doing some tests
        # scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        # hash = hashlib.sha256(update.message.text.encode()).hexdigest()
        # msg = f"{hash[-5:]} {update.message.text} - {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"

        await update.message.reply_text(f"{str(user)}")
