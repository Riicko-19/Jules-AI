from agents.manager import MANAGER_AGENT
import asyncio

async def test_agent():
    try:
        print("Testing agent run_async...")
        # Mocking input
        response = await MANAGER_AGENT.run_async(input="Hello, who are you?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())
