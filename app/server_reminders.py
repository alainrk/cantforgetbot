import log
from dotenv import load_dotenv
from firebase import Database
from models import Reminder
from telegram import __version__ as TG_VER
from telegram.ext import Application
import asyncio

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

    # Send reminder to user, delete reminder from db and update the key
    async def expired_reminder_handler(self, r: Reminder):
        text = f"📌 *Reminder* 📌\n\- {r.key}"
        if r.value:
            text += f"\n\- ||{r.value}||"
        return await self.application.bot.send_message(
            chat_id=r.chat_id,
            text=text,
            parse_mode="MarkdownV2"
        )

    async def run(self):
        rems = self.db.get_expired_reminders()

        rets = []
        for r in rems:
            # Run expired_reminder_handler in a separate thread in parallel
            rets.append(asyncio.create_task(self.expired_reminder_handler(r)))

        # await all tasks to finish
        await asyncio.gather(*rets)