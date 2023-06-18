import argparse
import os

import log
from dotenv import load_dotenv
from firebase import Database, DatabaseConfig
from server_bot import BotServer
from server_reminders import RemindersServer
import asyncio

firebaseProjectKeyFilename = "firebase-service-account-key.json"

load_dotenv()

logger = log.setup_logger(__name__)


def run_bot_server() -> None:
    logger.info("Starting bot server...")

    # Get envs and config
    token = os.getenv("TOKEN")

    # Setup firebase
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file_path = os.path.join(
        script_dir, "..", "data", firebaseProjectKeyFilename)
    db = Database(DatabaseConfig(key_file_path))

    # TODO: Setup config object

    app = BotServer(token, db)
    app.run()


def run_reminders_server() -> None:
    logger.info("Starting reminders server...")

    # Get envs and config
    token = os.getenv("TOKEN")

    # Setup firebase
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file_path = os.path.join(
        script_dir, "..", "data", firebaseProjectKeyFilename)
    db = Database(DatabaseConfig(key_file_path))

    # TODO: Setup config object

    app = RemindersServer(token, db)
    asyncio.run(app.run())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-server', action='store_true',
                        help='Run as bot server')
    parser.add_argument('--reminders-server',
                        action='store_true', help='Run as reminders server')

    args = parser.parse_args()
    if args.bot_server:
        run_bot_server()
    elif args.reminders_server:
        run_reminders_server()
    else:
        print("Please specify a server to run")
