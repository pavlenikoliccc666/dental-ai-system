
    



    

import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
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


# Učitaj vrijednosti iz lokalnog .env fajla.
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nije postavljen.")


# Ova lista određuje koje alate model smije zatražiti,
# a ToolNode koristi istu listu da ih izvrši.
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

# Model može vratiti običan tekst ili zahtjev da se izvrši neki alat.
model_with_tools = model.bind_tools(tools)


class AgentState(TypedDict):
    # add_messages spaja nove poruke s postojećom istorijom razgovora.
    messages: Annotated[list[AnyMessage], add_messages]


SYSTEM_PROMPT = """
You are a dental clinic receptionist.

You can answer questions using the available clinic tools.

Rules:
1. For clinic services, prices, or durations, use get_clinic_services_tool.
2. For available appointment times, use find_available_slots_tool.
3. For a dentist's working hours, use get_dentist_availability_tool.
4. For clinic FAQs and policies, use search_knowledge_tool.
5. Do not invent clinic facts, prices, policies, or appointment information.
6. If the tools do not provide the answer, say that you do not have that information.
"""


def call_model(state: AgentState) -> dict:
    """LangGraph node: send the conversation to the model once."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = model_with_tools.invoke(messages)

    # LangGraph doda ovu AI poruku u state["messages"].
    return {"messages": [response]}


# Napravi graph i registruj njegova dva čvora.
builder = StateGraph(AgentState)

builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

# Ova funkcija pogleda posljednju AI poruku:
# traži alat -> "tools"; nema zahtjeva za alatom -> END.
builder.add_conditional_edges("agent", tools_condition)

# Nakon izvršenog alata, model dobija rezultat i nastavlja razgovor.
builder.add_edge("tools", "agent")


# Pamti stanje razgovora prema thread_id.
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


def run_agent_once(user_message: str,thread_id: str) -> str:
    """Ulazna funkcija: pokreni graph za jednu korisničku poruku."""
    result = graph.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )

    # Posljednja poruka u završenom graph-u je konačan odgovor modela.
    return result["messages"][-1].content


if __name__ == "__main__":
    thread_id = "test-razgovor-1"

    print(run_agent_once("Zovi me Test Marko.", thread_id))
    print(run_agent_once("Kako se zovem?", thread_id))
    