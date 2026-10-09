from app.repositories.azure_chunk_repository import (
    AzureChunkRepository
)

from app.services.knowledge.entity_extractor import (
    EntityExtractor
)

from app.services.knowledge.graph_builder_service import (
    GraphBuilderService
)
import json



with open(
    "mock_chunks.json",
    "r",
    encoding="utf-8"
) as f:

    mock_results = json.load(f)


class GraphIngestionService:

    @staticmethod
    async def ingest_document(

        db,

        title: str

    ):

        document = (
            AzureChunkRepository
            .load_chunks_by_title(
                title
            )
        )

        if not document:

            raise Exception(
                "Document not found"
            )

        extractor = (
            EntityExtractor()
        )

        chunks = (
            document[
                "chunks"
            ]
        )

        for chunk in chunks:

            # result = await (
            #     extractor.extract(
            #         chunk[
            #             "content"
            #         ]
            #     )
            # )
            result = mock_results

            await (
                GraphBuilderService
                .process_chunk(

                    db=db,

                    chunk_id=
                    chunk[
                        "chunk_id"
                    ],

                    entities=
                    result[
                        "entities"
                    ],

                    relationships=
                    result[
                        "relationships"
                    ]
                )
            )

        return {

            "title":
            title,

            "chunks":
            len(
                chunks
            )
        }