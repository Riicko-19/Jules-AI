from google.adk.agents.llm_agent import Agent
from agents.tools import (
    run_powershell_command, check_disk_space, list_active_processes, monitor_gpu,
    get_recent_commits, summarize_pull_requests, read_active_issues,
    get_daily_schedule, book_meeting, search_web
)
import os

# Using gemini-1.5-flash as a practical default for sub-agents
# The prompt asked for "Gemini 3.0 Pro" for the ManagerAgent.
SUB_AGENT_MODEL = "gemini-1.5-flash"

try:
    SYSTEM_ADMIN_AGENT = Agent(
        name="SystemAdminAgent",
        model=SUB_AGENT_MODEL,
        instruction="You are a system administrator for a local Windows machine. You can run PowerShell commands to check system status. Ensure you do not run destructive commands.",
        tools=[run_powershell_command, check_disk_space, list_active_processes, monitor_gpu]
    )

    DEVOPS_AGENT = Agent(
        name="DevOpsAgent",
        model=SUB_AGENT_MODEL,
        instruction="You are a DevOps engineer managing GitHub repositories. The default repository is 'Ambica Patterns'. use tools to fetch information.",
        tools=[get_recent_commits, summarize_pull_requests, read_active_issues]
    )

    SCHEDULING_AGENT = Agent(
        name="SchedulingAgent",
        model=SUB_AGENT_MODEL,
        instruction="You are a personal scheduler. Manage the user's calendar using the provided tools.",
        tools=[get_daily_schedule, book_meeting]
    )

    INFO_AGENT = Agent(
        name="InfoAgent",
        model=SUB_AGENT_MODEL,
        instruction="You are a general knowledge assistant. Use the search tool to find real-time information.",
        tools=[search_web]
    )
except Exception as e:
    print(f"Error initializing sub-agents: {e}")
    # Fallback or re-raise
    raise e
