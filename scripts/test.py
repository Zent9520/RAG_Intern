from app.core.database import (
    AsyncSessionLocal
)

from app.services.knowledge.graph_completion_service import (
    GraphCompletionService
)


async def run():

    async with AsyncSessionLocal() as db:

        await (

            GraphCompletionService
            .run(
                db
            )
        )


if __name__ == "__main__":

    import asyncio

    asyncio.run(
        run()
    )