from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from app.read_knowledge import content_split, read_knowledge_file

load_dotenv()


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def embed_documents_chunks(chunks: list[str]):
    vector = embeddings.embed_documents(chunks)
    return vector






if __name__ == "__main__":
    content = read_knowledge_file()
    chunks = content_split(content)

    vectors = embed_documents_chunks(chunks)

    print("Broj chunkova:", len(chunks))
    print("Broj embeddinga:", len(vectors))
    print("Dimenzija jednog embeddinga:", len(vectors[0]))



if __name__ == "__main__":
    test_text = "Pacijent može otkazati termin 24 sata ranije."
    vector = embeddings.embed_query(test_text)

    print("Dimenzija embeddinga:", len(vector))
    print("Prvih 5 vrednosti:", vector[:5])