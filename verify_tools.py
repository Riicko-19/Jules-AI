from agents.tools import run_powershell_command, check_disk_space, list_active_processes, monitor_gpu, get_recent_commits, summarize_pull_requests, read_active_issues, get_daily_schedule, book_meeting, search_web

print("Verifying Tools...")

# System Admin Tools
print(f"PowerShell: {run_powershell_command('Get-Date')}")
print(f"Disk Space: {check_disk_space()}")
print(f"Processes: {list_active_processes()}")
print(f"GPU: {monitor_gpu()}")

# DevOps Tools (Will likely fail without token, but checks import/call)
print(f"Commits: {get_recent_commits()}")
print(f"PRs: {summarize_pull_requests()}")
print(f"Issues: {read_active_issues()}")

# Scheduling Tools
print(f"Schedule: {get_daily_schedule()}")
print(f"Book Meeting: {book_meeting('Meeting', '10:00 AM')}")

# Info Tools
print(f"Search: {search_web('Python FastAPI')}")

print("Verification Complete.")
