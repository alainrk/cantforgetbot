import logging
import os
import hashlib
import datetime
from dotenv import load_dotenv

from telegram import __version__ as TG_VER

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

from telegram import ForceReply, Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def isUserAllowed(user) -> bool:
    return user.username in os.getenv("USERS_ALLOWED").split(",")


async def authGuard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # TODO: Temp solution, check if user is allowed to use the bot
    if not isUserAllowed(update.effective_user):
        await update.message.reply_text("You are not allowed to use this bot")
        return False
    return True

# Define a few command handlers. These usually take the two arguments update and
# context.


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (await authGuard(update, context)):
        return

    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info("User %s started the conversation.", user)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (await authGuard(update, context)):
        return

    # Send a scheduled message in 10 minutes
    scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)

    """Echo the user message."""
    # Calculate hash of the message
    hash = hashlib.sha256(update.message.text.encode()).hexdigest()
    msg = f"{hash[-5:]} {update.message.text} - {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
    await update.message.reply_text(msg)


def main() -> None:
    # Get token from .env file
    token = os.getenv("TOKEN")

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
