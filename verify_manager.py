from agents.manager import MANAGER_AGENT

print(f"Manager: {MANAGER_AGENT.name}")
print(f"Model: {MANAGER_AGENT.model}")
if MANAGER_AGENT.sub_agents:
    print(f"Sub-Agents: {[a.name for a in MANAGER_AGENT.sub_agents]}")
else:
    print("No sub-agents found.")
