import asyncio

from loguru import logger

from Bot_API.settings_bot import start_bot


#####################################################
# Run the app
async def main() -> None:
    try:
        await start_bot()
    except Exception as ex:
        logger.exception(f'Disconnect {ex}')

if __name__ == "__main__":
    asyncio.run(main())



