from google.adk.agents.llm_agent import Agent
from agents.sub_agents import SYSTEM_ADMIN_AGENT, DEVOPS_AGENT, SCHEDULING_AGENT, INFO_AGENT

# The prompt requested "Gemini 3.0 Pro".
# Ensure this model is available in your Google Cloud project or use a fallback like "gemini-1.5-pro".
MANAGER_MODEL = "gemini-1.5-pro"

try:
    MANAGER_AGENT = Agent(
        name="ManagerAgent",
        model=MANAGER_MODEL,
        instruction="You are a helpful personal assistant. Delegate tasks to the appropriate sub-agents: SystemAdminAgent, DevOpsAgent, SchedulingAgent, InfoAgent. Maintain conversation history.",
        sub_agents=[SYSTEM_ADMIN_AGENT, DEVOPS_AGENT, SCHEDULING_AGENT, INFO_AGENT]
    )
except Exception as e:
    print(f"Error initializing ManagerAgent: {e}")
    raise e
