import re
import json

def parse_response(raw_llm_text):
    # This regex looks for CMD: {json} anywhere in the text
    pattern = re.compile(r'(ADD_TASK|CHECK_TASK|UPDATE_PROJECT|ADD_PROJECT|SCHEDULE_EVENT):\s*(\{.*?\})\s*(?=\n|$)', re.DOTALL)
    
    commands = []
    conversational_text = raw_llm_text
    
    for match in pattern.finditer(raw_llm_text):
        cmd = match.group(1)
        json_str = match.group(2)
        
        # FIX: Sanitize smart quotes (curly quotes) that phones auto-insert
        json_str = json_str.replace('“', '"').replace('”', '"')
        json_str = json_str.replace("‘", "'").replace("’", "'")
        
        try:
            data = json.loads(json_str)
            commands.append({"cmd": cmd, "data": data})
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse JSON for {cmd}: {json_str}")
        
        # Remove this specific command block from the conversational text
        conversational_text = conversational_text.replace(match.group(0), "").strip()
        
    # Clean up any extra newlines left over
    conversational_text = "\n".join([line for line in conversational_text.splitlines() if line.strip()])
    
    return conversational_text, commands