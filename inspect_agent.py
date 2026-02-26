from google.adk.agents.llm_agent import Agent
import inspect

print("Agent attributes:")
print(dir(Agent))
print("\nAgent constructor:")
print(inspect.signature(Agent.__init__))
