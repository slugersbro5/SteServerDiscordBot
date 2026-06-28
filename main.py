import asyncio
import os
from dotenv import load_dotenv


from core.bot import ServerBot
from core.logger import setup_logger

load_dotenv()
logger = setup_logger()


async def main():
    logger.info("=" * 50)
    logger.info("SESSY is waking up...")
    logger.info("=" * 50)

    bot = ServerBot()

    try:
        await bot.start(bot.config["discord_token"])

    except KeyboardInterrupt:
        logger.info("SESSY shutdown requested.")

    finally:
        logger.info("Closing Discord connection...")
        await bot.close()
        logger.info("SESSY stopped.")


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
