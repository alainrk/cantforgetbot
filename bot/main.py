import log
from bot import Bot
import os
from dotenv import load_dotenv

from firebase import DatabaseConfig, Database

firebaseProjectKeyFilename = "firebase-service-account-key.json"

load_dotenv()

logger = log.setup_logger(__name__)
logger.info("Starting bot")


def main() -> None:
    # Get envs and config
    token = os.getenv("TOKEN")

    # Setup firebase
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file_path = os.path.join(
        script_dir, "..", "data", firebaseProjectKeyFilename)
    db = Database(DatabaseConfig(key_file_path))

    # TODO: Setup config object

    bot = Bot(token, db)
    bot.run()


if __name__ == "__main__":
    main()
