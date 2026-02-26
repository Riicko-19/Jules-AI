from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import asyncio

async def test_runner():
    try:
        agent = Agent(name="TestAgent", model="gemini-1.5-flash", instruction="You are a helpful assistant.")
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, app_name="test_app", session_service=session_service, auto_create_session=True)

        print("Starting runner...")
        content = Content(role="user", parts=[Part(text="Hello")])
        async for event in runner.run_async(user_id="user1", session_id="session1", new_message=content):
            print(event)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_runner())
