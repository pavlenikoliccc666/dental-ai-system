import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from app.tools.appointments import (
 get_clinic_services_tool,
 get_dentist_availability_tool,
 get_patient_appointments_tool,
 find_available_slots_tool,
 reschedule_appointment_tool,
 book_appointment_tool,
 cancel_appointment_tool
)


load_dotenv()
from langchain_core.messages import (
    HumanMessage,
    ToolMessage
)

import json
from langchain_core.messages import ToolMessage

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY nije postavljen.")

tools = [get_clinic_services_tool,get_dentist_availability_tool,get_patient_appointments_tool,find_available_slots_tool,reschedule_appointment_tool,book_appointment_tool,cancel_appointment_tool]

model = ChatOpenAI(
    model = "gpt-5.6-luna",
    temperature=0,
    model_kwargs={"reasoning_effort": "none"}
)


model_with_tools = model.bind_tools(tools)


tool_registry = {
    current_tool.name : current_tool
    for current_tool in tools
}



def run_agent_once(user_message: str) -> str:
    messages = [
        HumanMessage(content=user_message)
    ]

    max_loops = 5

    for _ in range(max_loops):
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

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




if __name__ == "__main__":
    answer =run_agent_once("What services does clinic 1 have?")
    print(answer)
    
    

