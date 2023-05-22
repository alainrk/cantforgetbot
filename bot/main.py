import logging
import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (await authGuard(update, context)):
        return

    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (await authGuard(update, context)):
        return

    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    # Get token from .env file
    token = os.getenv("TOKEN")

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
