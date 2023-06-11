import log
from bot import Bot
import os
from dotenv import load_dotenv
import argparse

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-server', action='store_true',
                        help='Run as bot server')
    parser.add_argument('--reminders-server',
                        action='store_true', help='Run as reminders server')

    args = parser.parse_args()
    if args.bot_server:
        main()
    elif args.reminders_server:
        print("Still not implemented")
    else:
        print("Please specify a server to run")
