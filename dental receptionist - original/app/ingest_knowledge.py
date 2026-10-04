from sqlalchemy.orm import Session

from app.database import engine
from app.models import KnowledgeChunk
from app.create_embeddings import (
    embed_documents_chunks,
)
from app.read_knowledge import (
    read_knowledge_file,
    content_split,
)


def save_knowledge():
    content = read_knowledge_file()
    chunks = content_split(content)
    vectors = embed_documents_chunks(chunks)

    with Session(engine) as session:
        for chunk, vector in zip(chunks, vectors):
            knowledge_chunk = KnowledgeChunk(
                clinic_id = 1,
                content = chunk,
                source = "clinics_policies.txt",
                embedding = vector
            )
            session.add(knowledge_chunk)

        session.commit()


if __name__ == "__main__":
    save_knowledge()
    print("Knowledge successfully saved")
