import subprocess
import traceback

def push():
    try:
        # Check if already up to date or push
        result = subprocess.run(
            ["git", "push", "origin", "main"], 
            capture_output=True, 
            text=True,
            timeout=30 # Don't hang forever
        )
        with open("push_log.txt", "w") as f:
            f.write(f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\nCODE: {result.returncode}")
    except Exception as e:
        with open("push_log.txt", "w") as f:
            f.write(f"ERROR: {str(e)}\n{traceback.format_exc()}")

if __name__ == "__main__":
    push()
