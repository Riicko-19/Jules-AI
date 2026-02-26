from agents.sub_agents import SYSTEM_ADMIN_AGENT, DEVOPS_AGENT, SCHEDULING_AGENT, INFO_AGENT

print("Verifying Agents...")

agents = [SYSTEM_ADMIN_AGENT, DEVOPS_AGENT, SCHEDULING_AGENT, INFO_AGENT]

for agent in agents:
    print(f"Agent Name: {agent.name}")
    print(f"Agent Model: {agent.model}")
    # Handling potential different tool structures
    tools = getattr(agent, 'tools', [])
    tool_names = []
    if tools:
        for t in tools:
            if hasattr(t, '__name__'):
                tool_names.append(t.__name__)
            else:
                tool_names.append(str(t))
    print(f"Tools: {tool_names}")
    print("-" * 20)

print("Agent Verification Complete.")
