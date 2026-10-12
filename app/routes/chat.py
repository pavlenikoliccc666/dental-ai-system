
from app.schemas import Chat
from app.agent import run_agent_once
from fastapi import APIRouter, Request
from uuid import uuid4
from app.schemas import ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)
@router.post("/new", status_code=201)
def create_thread_id():
    thread_id = str(uuid4())

    return {"thread_id":thread_id}



@router.post("", status_code=201, response_model=ChatResponse)
def call_agent(request: Request, body: Chat, thread_id: str):
    graph = request.app.state.agent_graph
    reply = run_agent_once(body.message, thread_id, graph)

    return {
        "reply": reply,
        "thread_id": thread_id,
    }