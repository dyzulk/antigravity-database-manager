import os
import sys
import time
import subprocess

# Log file to see progress after IDE closes
log_file = r"C:\Users\dyzulk\.gemini\config\skills\antigravity-database-manager\scripts\delayed_recover.log"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

def is_ide_running():
    try:
        # Check tasklist for Antigravity IDE and Antigravity process names
        out = subprocess.check_output('tasklist', shell=True, text=True)
        return "Antigravity.exe" in out or "Antigravity IDE.exe" in out
    except Exception as e:
        log(f"Error checking processes: {e}")
        return False

def main():
    log("Started corrected delayed recovery daemon.")
    
    # Wait for IDE to close
    wait_count = 0
    while is_ide_running():
        if wait_count % 5 == 0:
            log("Waiting for Antigravity IDE to close...")
        time.sleep(1)
        wait_count += 1
        
    log("Antigravity IDE has closed! Waiting 3 seconds for file locks to release...")
    time.sleep(3)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "__main__.py")
    
    # Inherit full environment to preserve USERPROFILE for tilde (~) expansion
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Run recover
    log("Running recover...")
    cmd_recover = ['python', main_script, 'recover']
    res = subprocess.run(cmd_recover, env=env, capture_output=True, text=True)
    log(f"Recover Output:\n{res.stdout}\n{res.stderr}")
    
    # Run workspace migrate
    log("Running workspace migrate...")
    cmd_migrate = ['python', main_script, 'workspace', 'migrate', 'c:/Users/dyzulk/Documents/twinpath/icons']
    res = subprocess.run(cmd_migrate, env=env, capture_output=True, text=True)
    log(f"Migrate Output:\n{res.stdout}\n{res.stderr}")
    
    # Run auto rename
    log("Running auto rename...")
    auto_rename_script = os.path.join(script_dir, "auto_rename.py")
    cmd_rename = ['python', auto_rename_script]
    res = subprocess.run(cmd_rename, env=env, capture_output=True, text=True)
    log(f"Auto Rename Output:\n{res.stdout}\n{res.stderr}")
    
    log("Delayed recovery, migration, and auto-rename completed successfully! You can reopen the IDE now.")

if __name__ == '__main__':
    main()
