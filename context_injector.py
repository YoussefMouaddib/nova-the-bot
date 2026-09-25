from datetime import datetime
import database

def build_system_prompt():
    today = datetime.now().strftime("%A, %B %d, %Y")
    now = datetime.now().strftime("%I:%M %p")

    projects = database.get_active_projects()
    tasks = database.get_todays_tasks()

    project_block = "\n".join(
        [f"- {p['name']} ({p['status']}): Next step -> {p['next_step']}" for p in projects]
    ) if projects else "No active projects."

    task_block = "\n".join([f"- {t['title']}" for t in tasks]) if tasks else "No active tasks."

    prompt = f"""
SYSTEM PROMPT:
[redacted]

Today is {today}, and the time is {now}.

Here is my current project list:
{project_block}

Here are my active tasks:
{task_block}

--- INSTRUCTIONS ---
If I ask you to schedule something, add a task, or check off a task, output clearly structured commands at the end of your response in this exact format:

ADD_TASK: {{"Name": "...", "Done": false}}
CHECK_TASK: {{"title": "..."}}
SCHEDULE_EVENT: {{"title": "Event title", "date": "2025-06-19T15:00:00", "duration_minutes": 60}}

Only output a command when I clearly imply or agree on an action. 
Keep your conversational text brief and conversational. 
"""
    return prompt.strip()
