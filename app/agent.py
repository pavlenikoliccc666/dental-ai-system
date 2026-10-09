import os
from typing import Annotated,Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
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
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from app.tools.knowledge import search_knowledge_tool
load_dotenv()
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
    SystemMessage,
    AnyMessage
)
import json
from langchain_core.messages import ToolMessage

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nije postavljen.")

tools = [search_knowledge_tool,get_clinic_services_tool,get_dentist_availability_tool,get_patient_appointments_tool,find_available_slots_tool,reschedule_appointment_tool,book_appointment_tool,cancel_appointment_tool]

model = ChatOpenAI(
    model = "gpt-5.6-luna",
    temperature=0,
    model_kwargs={"reasoning_effort": "none"}
)

class AgentState(TypedDict):
    messages : Annotated[list[AnyMessage],add_messages]


model_with_tools = model.bind_tools(tools)


tool_registry = {
    current_tool.name : current_tool
    for current_tool in tools
}


SYSTEM_PROMPT = """
You are dental receptionist agent.You have accsess to multiple tools that can help you answer
questions about dental clinic services,
dentist availability, patient appointments, and scheduling. Use the tools as needed to provide accurate and helpful responses to user queries.
If you dont have answer to the question, use the tools to find the answer.If after that you still dont have answer, say "I'm sorry, I don't have that information available at
the moment." and do not make up an answer.

Rules:

1. If question is about clinic services,prices or duration about service, use get_clinic_services_tool.


2. If question is about free slots use find available_slots_tool.

3. If question is about dentist availability, use get_dentist_availability_tool.

4.If question is about FAQS and policies,or general knowledge about dental clinic, use search_knowledge_tool.

5. If tool doesnt have answer, say "I'm sorry, I don't have that information available at the moment." and do not make up an answer.


"""


def run_agent_once(user_message: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    max_loops = 5

    for _ in range(max_loops):
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content,"over"
        
       return "tools"

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            selected_tool = tool_registry.get(tool_name)

            if selected_tool is None:
                raise RuntimeError(
                    f"Tool '{tool_name}' nije pronađen."
                )

            tool_result = selected_tool.invoke(tool_args)

            messages.append(
                ToolMessage(
                    content=json.dumps(tool_result, default=str),
                    tool_call_id=tool_call["id"],
                )
            )

    raise RuntimeError(
        "Agent je dostigao maksimalan broj koraka bez konačnog odgovora."
    )



builder = StateGraph(AgentState)

builder.add_node("call node",run_agent_once)
builder.add_node("tools",ToolNode(tools))

builder.add_edge(START,"call node")

builder.add_conditional_edge("tools",
tools)

builder.add_edge("call node",END)

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer,
)

initial_state = {
    "messages":[
        HumanMessage(content="What services does clinic 1 have?")
    ]
}



if __name__ == "__main__":
    answer = graph.invoke(initial_state)
    print(answer)
    
    



    

