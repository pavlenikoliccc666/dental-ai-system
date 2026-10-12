import os
from typing import Annotated
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from app.tools.appointments import (
    get_clinic_services_tool,
    get_dentist_availability_tool,
    get_patient_appointments_tool,
    find_available_slots_tool,
    reschedule_appointment_tool,
    book_appointment_tool,
    cancel_appointment_tool,
)
from app.tools.knowledge import search_knowledge_tool


# Učitaj DATABASE_URL i OPENAI_API_KEY iz .env fajla.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL nije postavljen.")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nije postavljen.")

# SQLAlchemy URL koji koristi tvoj app počinje sa:
# postgresql+psycopg://
#
# PostgresSaver koristi psycopg direktno i očekuje:
# postgresql://
#
# Zato pravimo posebnu varijablu. DATABASE_URL ne mijenjamo.
if DATABASE_URL.startswith("postgresql+psycopg://"):
    CHECKPOINT_DATABASE_URL = DATABASE_URL.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
else:
    CHECKPOINT_DATABASE_URL = DATABASE_URL


tools = [
    search_knowledge_tool,
    get_clinic_services_tool,
    get_dentist_availability_tool,
    get_patient_appointments_tool,
    find_available_slots_tool,
    reschedule_appointment_tool,
    book_appointment_tool,
    cancel_appointment_tool,
]


model = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0,
    model_kwargs={"reasoning_effort": "none"},
)

model_with_tools = model.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


SYSTEM_PROMPT = """
You are a dental clinic receptionist.

Use the available tools for current clinic information.

Rules:
1. For clinic services, prices, or duration, use get_clinic_services_tool.
2. For available appointment times, use find_available_slots_tool.
3. For dentist working hours, use get_dentist_availability_tool.
4. For clinic FAQs and policies, use search_knowledge_tool.
5. Do not invent clinic facts, prices, policies, or appointment information.
6. If the tools do not provide an answer, say you do not have that information.
"""


def call_model(state: AgentState) -> dict:
    """Jedan korak: pošalji razgovor modelu i vrati njegovu poruku."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = model_with_tools.invoke(messages)

    # LangGraph će ovu poruku dodati u stanje razgovora.
    return {"messages": [response]}

builder = StateGraph(AgentState)

builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

# Tool call -> tools node; običan odgovor -> kraj.
builder.add_conditional_edges("agent", tools_condition)

# Poslije alata graph se vraća modelu.
builder.add_edge("tools", "agent") 
@asynccontextmanager
async def lifespan(app: FastAPI):
         
     with PostgresSaver.from_conn_string(CHECKPOINT_DATABASE_URL) as checkpointer:
                checkpointer.setup()

                graph = builder.compile(checkpointer=checkpointer)

                app.state.agent_graph = graph

                
            
               
                yield

    
        

                



def run_agent_once(user_message: str, thread_id: str,graph) -> str:
    """Pokreni graph za jednu poruku i vrati konačni odgovor."""
        

    result = graph.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

    return result["messages"][-1].content







if __name__ == "__main__":
    thread_id = "test-razgovor-1"

    
