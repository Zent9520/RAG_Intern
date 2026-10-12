from backend.app.repositories.knowledge_graph.graph_repository import (
    GraphRepository
)


class GraphVisualizationService:

    @staticmethod
    async def get_graph(

        db

    ):

        return await (

            GraphRepository
            .get_graph(
                db
            )
        )