import uuid
import asyncio
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types
from google.adk.events import Event

# --- Define Tool Functions ---
def booking_handler(request: str) -> str:
    """
    Handles booking requests for flights and hotels.
    Args:
        request: The user's request for a booking.
    Returns:
        A confirmation message that the booking was handled.
    """
    print(f"----- Tool: booking_handler called with request: '{request}' -----")
    return f"Booking action for '{request}' has been successfully handled."

def info_handler(request: str) -> str:
    """
    Handles general information requests.
    Args:
        request: The user's question.
    Returns:
        A message indicating the information request was handled.
    """
    print(f"----- Tool: info_handler called with request: '{request}' -----")
    return f"Information request for '{request}'. Result: Simulated information retrieval complete."

# --- Create Tools from Functions ---
booking_tool = FunctionTool(booking_handler)
info_tool = FunctionTool(info_handler)

# --- Define Specialized Sub-Agents ---
booking_agent = Agent(
    name='Booker',
    model="gemini-2.5-flash",
    description="A specialized agent that handles all flight and hotel booking requests by calling the booking tool.",
    tools=[booking_tool]
)

info_agent = Agent(
    name="Info",
    model="gemini-2.5-flash",
    description="A specialized agent that provides general information and answers user questions by calling the info tool.",
    tools=[info_tool]
)

# --- Define the Parent (Coordinator) Agent ---
# The coordinator's instructions are refined to be more direct about its delegation role.
coordinator = Agent(
    name="Coordinator",
    model="gemini-2.5-flash",
    instruction=(
        "You are the main coordinator for a multi-agent system. Your only task is to analyze incoming user requests "
        "and delegate them to the appropriate specialist agent. Do not try to answer the user directly.\n"
        "- If the request is about booking flights or hotels, delegate to the 'Booker' agent.\n"
        "- If the request is a general information question, delegate to the 'Info' agent.\n"
        "If the request is unclear or doesn't fit these categories, ask the user for clarification."
    ),
    description="A coordinator that routes user requests to the correct specialist agent.",
    sub_agents=[booking_agent, info_agent]
)

# --- Asynchronous Execution Logic ---
# This async function aligns with ADK documentation best practices.
async def run_coordinator_async(runner: Runner, request: str, session_id: str):
    """Runs the coordinator agent with a given request and prints the final response."""
    print(f"\n--- Running Coordinator with request: '{request}' ---")
    user_id = "user_123"
    final_result = "Agent did not produce a final response."

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=request)])

    # The run_async method executes the agent and yields events.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # Optional: Print all events to see the full execution flow, including delegation
        # print(f" [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}")

        # is_final_response() marks the concluding message for the turn.
        if event.is_final_response() and event.content and event.content.parts:
            final_result = event.content.parts[0].text
            break # Stop processing once the final response is found

    print(f"Coordinator Final Response: {final_result}")
    return final_result

async def main():
    """Main async function to run the ADK example."""
    print("--- Google ADK Routing Example (Async Auto-Flow) ---")
    print("Note: This requires Google ADK installed and authenticated.")

    # A single SessionService and Runner can be used for multiple conversations.
    session_service = InMemorySessionService()
    runner = Runner(agent=coordinator, app_name="routing_app", session_service=session_service)
    
    # Create unique sessions for each independent conversation flow
    session_a = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="user_123", session_id=session_a)
    result_a = await run_coordinator_async(runner, "Book me a hotel in Paris.", session_a)
    print(f"Final Output A: {result_a}")

    session_b = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="user_123", session_id=session_b)
    result_b = await run_coordinator_async(runner, "What is the highest mountain in the world?", session_b)
    print(f"Final Output B: {result_b}")
    
    session_c = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="user_123", session_id=session_c)
    result_c = await run_coordinator_async(runner, "Tell me a random fact.", session_c)
    print(f"Final Output C: {result_c}")

    session_d = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="user_123", session_id=session_d)
    result_d = await run_coordinator_async(runner, "Find flights to Tokyo next month.", session_d)
    print(f"Final Output D: {result_d}")


if __name__ == "__main__":
    # In a standard Python script, you use asyncio.run() to execute the main async function.
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")