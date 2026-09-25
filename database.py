from notion_client import Client
import config

notion = Client(auth=config.NOTION_API_KEY)

def get_active_projects():
    projects = []
    next_cursor = None

    while True:
        response = notion.databases.query(
            database_id=config.NOTION_PROJECTS_DB_ID,
            filter={"property": "Status", "status": {"equals": "In progress"}},
            start_cursor=next_cursor,
            page_size=100
        )

        for result in response["results"]:
            props = result["properties"]
            title = props["Project Name"]["title"][0]["text"]["content"]
            status = props["Status"]["status"]["name"]
            tags = ", ".join([t["name"] for t in props.get("Tags", {}).get("multi_select", [])])
            last_step = props.get("Last Step", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            next_step = props.get("Next Step", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
            summary = props.get("Summary", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")

            projects.append({
                "name": title, "status": status, "tags": tags,
                "last_step": last_step, "next_step": next_step, "summary": summary
            })

        if not response.get("has_more"):
            break
        next_cursor = response.get("next_cursor")

    return projects

def get_todays_tasks():
    tasks = []
    next_cursor = None

    while True:
        response = notion.databases.query(
            database_id=config.NOTION_TASKS_DB_ID,
            filter={"property": "Done", "checkbox": {"equals": False}},
            start_cursor=next_cursor,
            page_size=100
        )

        for result in response["results"]:
            props = result["properties"]
            title = props["Name"]["title"][0]["text"]["content"]
            tasks.append({"title": title})

        if not response.get("has_more"):
            break
        next_cursor = response.get("next_cursor")

    return tasks