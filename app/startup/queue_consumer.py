import asyncio

from app.workers.review_worker import review_worker


async def start_queue_consumers() -> None:
    asyncio.create_task(
        review_worker(),
    )