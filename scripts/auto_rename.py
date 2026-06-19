import os
import json
import re
import sys
import subprocess
import urllib.request
import urllib.error
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime, timezone, timedelta

# Resolve paths
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config", "settings.json")
manager_script = os.path.join(script_dir, "__main__.py")

# Dynamic discovery of Brain directory
sys.path.append(script_dir)
try:
    from src.core.environment import EnvironmentResolver
    brain_dir = os.path.join(EnvironmentResolver.get_gemini_base_path(), "brain")
except Exception:
    home = os.path.expanduser("~")
    primary_brain = os.path.join(home, ".gemini", "antigravity-ide", "brain")
    fallback_brain = os.path.join(home, ".gemini", "antigravity", "brain")
    brain_dir = fallback_brain if not os.path.exists(primary_brain) and os.path.exists(fallback_brain) else primary_brain

def load_config():
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_request_text(text):
    # Strip XML tags (like <USER_REQUEST>)
    text = re.sub(r'<[^>]+>', '', text)
    # Strip markdown code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Strip mentions
    text = re.sub(r'@\[[^\]]+\]', '', text)
    return " ".join(text.split()).strip()

def get_gemini_title(api_key, model_name, request_text, max_len):
    cleaned = clean_request_text(request_text)
    if not cleaned:
        return "Untitled Conversation"
        
    prompt = (
        "Summarize the following developer request into a clean, concise, and professional title "
        "(in English or Indonesian, matching the request's language).\n"
        "Strict rules:\n"
        "1. Do NOT include conversational filler (e.g. 'how to', 'please help me', 'saya ingin', 'bagaimana cara', 'tolong').\n"
        f"2. Keep it under {max_len} characters.\n"
        "3. Do NOT wrap in quotes.\n"
        "4. Output ONLY the title, nothing else.\n\n"
        f"Developer Request:\n{cleaned}"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers=headers,
        method="POST"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                title = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                title = title.replace('"', '').replace("'", "").strip()
                title = re.sub(r'^#\s*', '', title)
                if len(title) > max_len:
                    title = title[:max_len-3] + "..."
                return title
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = (attempt + 1) * 8
                print(f"  [429 Rate Limit] Waiting {wait_time}s to retry...")
                time.sleep(wait_time)
                continue
            print(f"  [API Error] HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"  [API Error] {e}")
            return None
    return None

def update_task_md(uuid_dir, title):
    task_md_path = os.path.join(uuid_dir, "task.md")
    try:
        if os.path.exists(task_md_path):
            with open(task_md_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # If it already starts with a title, replace the first line
            if lines and lines[0].startswith("#"):
                lines[0] = f"# {title}\n"
            else:
                lines.insert(0, f"# {title}\n\n")
                
            with open(task_md_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        else:
            with open(task_md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n- `[ ]` task list\n")
        return True
    except Exception as e:
        print(f"  [Error] Failed to update task.md: {e}")
        return False

def is_generic_title(title):
    if not title:
        return True
    title_clean = title.strip().lower()
    # Check for various generic names
    if title_clean in ["", "untitled", "(untitled)", "untitled conversation", "recovered", "conversation", "task list", "tasks"]:
        return True
    # Check if it starts with Conversation and some ID/date
    if title_clean.startswith("conversation ") or title_clean.startswith("conversation("):
        return True
    return False

def process_conversation(uuid, db_title, api_key, model_name, max_len):
    uuid_dir = os.path.join(brain_dir, uuid)
    transcript_path = os.path.join(uuid_dir, ".system_generated", "logs", "transcript.jsonl")
    
    if not os.path.exists(transcript_path):
        return None
        
    first_user_input = ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                if obj.get("type") == "USER_INPUT":
                    first_user_input = obj.get("content", "")
                    break
    except Exception:
        return None
        
    if not first_user_input:
        return None
        
    # Check database title: if it already has a non-generic title, skip renaming entirely!
    if not is_generic_title(db_title):
        return None
        
    existing_title = None
    task_md_path = os.path.join(uuid_dir, "task.md")
    if os.path.exists(task_md_path):
        try:
            with open(task_md_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    candidate = first_line[2:].strip()
                    if not is_generic_title(candidate):
                        existing_title = candidate
        except Exception:
            pass
            
    if existing_title:
        return (uuid, existing_title, True) # Reused
        
    # Get Gemini title
    new_title = get_gemini_title(api_key, model_name, first_user_input, max_len)
    if not new_title:
        return None
        
    update_task_md(uuid_dir, new_title)
    return (uuid, new_title, False)

def main():
    print("==================================================")
    print("  Antigravity AI-Powered Parallel Auto-Renamer")
    print("==================================================")
    
    config = load_config()
    api_key = config.get("gemini_api_key")
    model_name = config.get("model_name", "gemini-2.5-flash")
    max_len = config.get("max_title_length", 40)
    
    if not api_key:
        print("Error: gemini_api_key not found in config.")
        sys.exit(1)
        
    if not os.path.exists(brain_dir):
        print(f"Error: Brain directory not found at {brain_dir}")
        sys.exit(1)
        
    # Import scanner module dynamically
    try:
        from src.core.db_scanner import list_conversations
        db_path = EnvironmentResolver.get_antigravity_db_path()
    except Exception as e:
        print(f"Error loading database modules: {e}")
        sys.exit(1)
        
    # Load all existing conversation titles from the SQLite database
    db_titles = {}
    if os.path.exists(db_path):
        try:
            convs = list_conversations(db_path)
            db_titles = {c.uuid: c.title for c in convs}
            print(f"Loaded {len(db_titles)} conversation titles from database index.")
        except Exception as e:
            print(f"Warning: Failed to load database titles: {e}")
            
    # Scan brain directories for UUIDs
    uuids = []
    for d in os.listdir(brain_dir):
        if os.path.isdir(os.path.join(brain_dir, d)) and len(d) == 36 and "-" in d:
            uuids.append(d)
            
    print(f"Found {len(uuids)} conversation folders in brain.")
    
    results = []
    max_workers = 10
    print(f"Processing in parallel using {max_workers} worker threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_uuid = {
            executor.submit(
                process_conversation, 
                uuid, 
                db_titles.get(uuid), 
                api_key, 
                model_name, 
                max_len
            ): uuid 
            for uuid in uuids
        }
        
        completed = 0
        for future in as_completed(future_to_uuid):
            completed += 1
            uuid = future_to_uuid[future]
            try:
                res = future.result()
                if res:
                    results.append(res)
                    _, title, reused = res
                    tag = "[REUSED]" if reused else "[AI GENERATED]"
                    print(f"  [{completed}/{len(uuids)}] Processed {uuid[:8]}: {tag} {title}")
                else:
                    # Not printed if skipped because it already has a good name
                    pass
            except Exception as e:
                print(f"  [{completed}/{len(uuids)}] Error in {uuid[:8]}: {e}")
                
    if not results:
        print("\nAll active conversations already have descriptive titles. No updates needed.")
        return
        
    print("\nUpdating database index sequentially...")
    renamed_count = 0
    for idx, (uuid, title, reused) in enumerate(results, start=1):
        # Rename in active database index
        cmd = ["python", manager_script, "conversations", "rename", uuid, title]
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if res.returncode == 0:
            renamed_count += 1
        else:
            print(f"  Failed to rename database index for {uuid[:8]}: {res.stderr.strip()}")
            
        if idx % 10 == 0 or idx == len(results):
            print(f"  Database sync: {idx}/{len(results)} updated.")
            
    print(f"\n==================================================")
    print(f"Finished auto-renaming. Database updated: {renamed_count}")
    print("==================================================")

if __name__ == "__main__":
    main()
