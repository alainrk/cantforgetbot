import os
import hashlib
import datetime
from dotenv import load_dotenv

import log
from bot import Bot

load_dotenv()


def main() -> None:
    # Get envs and config
    token = os.getenv("TOKEN")

    # TODO: Setup config object

    logger = log.setup_logger(__name__)
    logger.info("Starting bot")

    bot = Bot(token)
    bot.run()


if __name__ == "__main__":
    main()
