import subprocess

def check():
    with open("check_git.txt", "w") as f:
        try:
            status = subprocess.check_output(["git", "status"], text=True)
            f.write("STATUS:\n" + status + "\n")
        except Exception as e:
            f.write(f"STATUS ERROR: {e}\n")
            
        try:
            log = subprocess.check_output(["git", "log", "-1"], text=True)
            f.write("LOG:\n" + log + "\n")
        except Exception as e:
            f.write(f"LOG ERROR: {e}\n")

if __name__ == "__main__":
    check()
