import subprocess
import os
from github import Github
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

# System Admin Tools
DESTRUCTIVE_COMMANDS = ["format", "rm -rf", "del /s", "rd /s"]

def run_powershell_command(command: str) -> str:
    """Runs a PowerShell command and returns the output.

    Args:
        command: The PowerShell command to run.
    """
    for cmd in DESTRUCTIVE_COMMANDS:
        if cmd in command.lower():
            return f"Error: Command '{command}' is considered destructive and blocked."

    try:
        # Check if running on Windows
        if os.name == 'nt':
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            return result.stdout or result.stderr
        else:
            return f"Mock output for command: {command} (Simulating Windows environment on Linux)"
    except Exception as e:
        return f"Error executing command: {e}"

def check_disk_space() -> str:
    """Checks disk space."""
    return run_powershell_command("Get-PSDrive -PSProvider FileSystem")

def list_active_processes() -> str:
    """Lists active processes."""
    return run_powershell_command("Get-Process | Select-Object -First 10")

def monitor_gpu() -> str:
    """Monitors Intel Arc GPU usage."""
    # Assuming Intel Arc GPU metrics are available via a specific command or tool
    # Using a placeholder command since specific Intel Arc cmdlets might vary
    return run_powershell_command("Get-CimInstance Win32_VideoController | Select-Object Name, Status, DriverVersion")

# DevOps Tools
def get_recent_commits(repo_name: str = "Ambica Patterns") -> str:
    """Fetches recent commits for a repository.

    Args:
        repo_name: The name of the repository (default: 'Ambica Patterns').
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN not set."

    g = Github(token)
    try:
        # Assuming the repo is accessible to the authenticated user
        # Try to get repo by name, might need full name 'user/repo'
        # For this mock, we'll try to search or just use the string if it looks like 'user/repo'
        if "/" in repo_name:
             repo = g.get_repo(repo_name)
        else:
            # Search for the repo in the user's repos
            user = g.get_user()
            try:
                repo = user.get_repo(repo_name)
            except:
                # Fallback: search globally or assume user/repo format wasn't provided correctly
                return f"Error: Could not find repository '{repo_name}'. Please provide 'owner/repo'."

        commits = repo.get_commits()[:5]
        return "\n".join([f"{c.sha[:7]}: {c.commit.message}" for c in commits])
    except Exception as e:
        return f"Error fetching commits: {e}"

def summarize_pull_requests(repo_name: str = "Ambica Patterns") -> str:
    """Summarizes open pull requests for a repository.

    Args:
        repo_name: The name of the repository.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN not set."

    g = Github(token)
    try:
        if "/" in repo_name:
             repo = g.get_repo(repo_name)
        else:
            user = g.get_user()
            try:
                repo = user.get_repo(repo_name)
            except:
                 return f"Error: Could not find repository '{repo_name}'."

        prs = repo.get_pulls(state='open')
        return "\n".join([f"#{pr.number}: {pr.title}" for pr in prs])
    except Exception as e:
        return f"Error fetching PRs: {e}"

def read_active_issues(repo_name: str = "Ambica Patterns") -> str:
    """Reads active issues for a repository.

    Args:
        repo_name: The name of the repository.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN not set."

    g = Github(token)
    try:
        if "/" in repo_name:
             repo = g.get_repo(repo_name)
        else:
            user = g.get_user()
            try:
                repo = user.get_repo(repo_name)
            except:
                 return f"Error: Could not find repository '{repo_name}'."

        issues = repo.get_issues(state='open')
        return "\n".join([f"#{issue.number}: {issue.title}" for issue in issues])
    except Exception as e:
        return f"Error fetching issues: {e}"


# Scheduling Tools
def get_daily_schedule() -> str:
    """Gets the daily schedule."""
    return "9:00 AM - Team Sync\n11:00 AM - Client Call\n2:00 PM - Focus Time"

def book_meeting(title: str, time: str) -> str:
    """Books a meeting.

    Args:
        title: The title of the meeting.
        time: The time of the meeting.
    """
    return f"Meeting '{title}' booked for {time}."

# Info Tools
def search_web(query: str) -> str:
    """Searches the web for information.

    Args:
        query: The search query.
    """
    try:
        results = DDGS().text(query, max_results=3)
        return "\n".join([f"{r['title']}: {r['href']}\n{r['body']}" for r in results])
    except Exception as e:
        return f"Error searching web: {e}"
