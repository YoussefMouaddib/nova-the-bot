import local_commands

def execute_commands(commands_list):
    for command in commands_list:
        cmd = command["cmd"]
        data = command["data"]
        
        try:
            if cmd == "ADD_TASK":
                local_commands.add_task(data)
            elif cmd == "CHECK_TASK":
                local_commands.check_task(data)
            elif cmd == "UPDATE_PROJECT":
                local_commands.update_project(data)
            elif cmd == "ADD_PROJECT":
                local_commands.add_project(data)
            elif cmd == "SCHEDULE_EVENT":
                local_commands.schedule_gcal_event(
                    title=data["title"],
                    start_time_str=data["date"],
                    duration_minutes=data.get("duration_minutes", 60)
                )
            else:
                print(f"⚠️ Unknown command: {cmd}")
        except Exception as e:
            print(f"❌ Error executing {cmd}: {e}")