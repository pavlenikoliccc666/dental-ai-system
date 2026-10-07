from app.search_knowledge import search_knowledge
from langchain_core.tools import tool

@tool
def search_knowledge_tool(query: str, clinic_id: int, limit: int = 3) -> list[dict]:
    """This tool returns the most relevant knowledge chunks based on the query and clinic ID."""
    
    results = search_knowledge(query, clinic_id, limit)

    return [
    {
        "content": result.content,
        "source": result.source,
        "clinic_id": result.clinic_id,
    }
    for result in results
]