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


def isUserAllowed(user) -> bool:
    return user.username in os.getenv("USERS_ALLOWED").split(",")


async def authGuard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # TODO: Temp solution, check if user is allowed to use the bot
    if not isUserAllowed(update.effective_user):
        await update.message.reply_text("You are not allowed to use this bot")
        return False
    return True


class Bot:
    def __init__(self, token, db: Database):
        self.db = db
        self.application = Application.builder().token(token).build()
        self.__set_handlers()

    def __set_handlers(self):
        self.application.add_handler(
            CommandHandler("start", self.__start_handler))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.__text_handler))

    def run(self):
        self.application.run_polling()

    async def __text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not (await authGuard(update, context)):
            return

        # XXX: Doing some tests
        scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        hash = hashlib.sha256(update.message.text.encode()).hexdigest()
        msg = f"{hash[-5:]} {update.message.text} - {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"

        self.db.test(msg)

        await update.message.reply_text(msg)

    async def __start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not (await authGuard(update, context)):
            return

        """Send a message when the command /start is issued."""
        user = update.effective_user
        logger.info(f"User {user} started the conversation.")
        try:
            await update.message.reply_text(f"Hi {user.full_name}!")
        except Exception as e:
            logger.error(f"Error while sending message: {e}")
