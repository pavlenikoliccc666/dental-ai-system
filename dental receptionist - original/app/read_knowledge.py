from pathlib import Path

def read_knowledge_file():
    path = Path("knowledge/clinics_policies.txt")
    content = path.read_text(encoding="utf-8")
    return content



def content_split(content: str):
    chunks_v1 = content.split("---")
    clean_chunks = []

    for chunk in chunks_v1:
        clean_chunk = chunk.strip()

        if len(clean_chunk) > 0:
            clean_chunks.append(clean_chunk)

    return clean_chunks


if __name__ == "__main__":
    text = read_knowledge_file()
    chunks = content_split(content = text)
    
    print(chunks)