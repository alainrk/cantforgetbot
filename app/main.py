import argparse
import os

import log
from dotenv import load_dotenv
from firebase import Database, DatabaseConfig
from server_bot import BotServer
from server_reminders import RemindersServer


import asyncio
import threading
from aiohttp import web


firebaseProjectKeyFilename = "firebase-service-account-key.json"

load_dotenv()

logger = log.setup_logger(__name__)


async def healthcheck(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/healthcheck', healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

def run_webserver():
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(start_webserver())
    asyncio.get_event_loop().run_forever()


def run_bot_server() -> None:
    logger.info("Starting bot server...")

    # Get envs and config
    token = os.getenv("TOKEN")

    # Setup firebase
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file_path = os.path.join(
        script_dir, "..", firebaseProjectKeyFilename)
    db = Database(DatabaseConfig(key_file_path))

    # TODO: Setup config object

    app = BotServer(token, db)
    app.run()


def run_reminders_server() -> None:
    logger.info("Starting reminders server...")

    # Get envs and config
    token = os.getenv("TOKEN")

    # Get reminders occurrence frequency
    occurrences = os.getenv("REMINDERS_EXPIRATIONS_MINUTES")
    if occurrences is None:
        logger.error("No reminders occurrence frequency specified")
        return
    occurrence_map_minutes = list(map(int, occurrences.split(",")))

    # Setup firebase
    script_dir = os.path.dirname(os.path.realpath(__file__))
    key_file_path = os.path.join(
        script_dir, "..", firebaseProjectKeyFilename)
    db = Database(DatabaseConfig(key_file_path))

    # TODO: Setup config object

    app = RemindersServer(token, db, occurrence_map_minutes)
    asyncio.run(app.run())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bot-server', action='store_true',
                        help='Run as bot server')
    parser.add_argument('--reminders-server',
                        action='store_true', help='Run as reminders server')
    args = parser.parse_args()

    webserver_thread = threading.Thread(target=run_webserver)
    webserver_thread.start()

    if args.bot_server:
        run_bot_server()
    elif args.reminders_server:
        run_reminders_server()
    else:
        print("Please specify a server to run")
        exit(1)

    webserver_thread.join()

if __name__ == "__main__":
    main()