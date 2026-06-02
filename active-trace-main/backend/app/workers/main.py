import asyncio
import logging

logger = logging.getLogger(__name__)

async def main() -> None:
    logger.info("Worker placeholder started. Loop no-op.")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
