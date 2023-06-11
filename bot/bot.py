from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import __version__ as TG_VER
import os
import hashlib
import datetime
from dotenv import load_dotenv
from firebase import Database

from models import User, Context, Message, Step

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


def is_command(text: str) -> bool:
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

    async def __auth_guard(self, update: Update) -> bool:
        def is_user_allowed(user) -> bool:
            return user.username in os.getenv("USERS_ALLOWED").split(",")

        # TODO: Temp solution, check if user is allowed to use the bot
        if not is_user_allowed(update.effective_user):
            await update.message.reply_text("You are not allowed to use this bot")
            return False
        return True

    async def __process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not (await self.__auth_guard(update)):
            return

        # User retrieval
        user = self.db.get_user(update.effective_user.username)
        if not user:
            user = self.db.add_user(
                User(
                    update.effective_user.id,
                    update.effective_user.first_name,
                    update.effective_user.last_name,
                    update.effective_user.username,
                    Context()
                )
            )

        # TODO: Move and place this stuff properly

        print(update.message)

        # Step execution
        if is_command(update.message.text):
            # /debug command is executed before anything else and does not have side effects
            if update.message.text == "/debug":
                await update.message.reply_text(f"{user}")
                return

            # Set last step and message
            user.context.last_step = Step(
                top_level=True, is_command=True, code=update.message.text[1:])
            user.context.last_message = Message(
                is_command=True, text=update.message.text)

            # /start command
            if user.context.last_step.code == "start":
                await update.message.reply_text(f"Welcome {user.firstname}!")
                self.db.update_user(user.username, user)
                return
            # Any other command
            await update.message.reply_text(f"Unknown command")
            self.db.update_user(user.username, user)
            return
        else:
            previous_step = user.context.last_step
            previous_message = user.context.last_message

            ############################
            # New key to save
            ############################

            # If user is in top level, then it's a new key to save
            if previous_step.top_level:
                key = update.message.text
                reply_keyboard = [["Save"], ["Add Value"], ["Cancel"]]
                reply_markup = ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True)

                await update.message.reply_text(f"Saving \"{key}\" in your repetitions...", reply_markup=reply_markup)

                user.context.last_step = Step(
                    top_level=False, is_command=False, code="key-given")

                user.context.last_message = Message(
                    is_command=False, text=update.message.text)

                self.db.update_user(user.username, user)

                return

            ############################
            # Button: Save
            ############################

            ############################
            # Button: Add Value
            ############################

            ############################
            # Button: Cancel
            ############################

            await update.message.reply_text(f"Echo: {update.message.text}")
            self.db.update_user(user.username, user)
            return

        # XXX: Doing some tests
        # scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        # hash = hashlib.sha256(update.message.text.encode()).hexdigest()
        # msg = f"{hash[-5:]} {update.message.text} - {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
