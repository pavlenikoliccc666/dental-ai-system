from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models import KnowledgeChunk
from app.create_embeddings import embeddings


def search_knowledge(
    query: str,
    clinic_id: int,
    limit: int = 3,
):
    query_embedding = embeddings.embed_query(query)

    with Session(engine) as session:
        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.clinic_id == clinic_id)
            .order_by(
                KnowledgeChunk.embedding.cosine_distance(query_embedding)
            )
            .limit(limit)
        )

        results = session.scalars(stmt).all()

    return results

if __name__ == "__main__":
    results = search_knowledge(
        query="Kako mogu da otkažem termin?",
        clinic_id=1,
        limit=3,
    )

    for result in results:
        print(result.content)
        print("---")