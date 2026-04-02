import os
import subprocess

def run_git():
    commands = [
        "git init",
        "git add .",
        "git config user.name \"Soham\"",
        "git config user.email \"soham@student.university.edu\"",
        "git commit -m \"chore: Initialize Professional MLOps Repository and Dashboard\"",
        "git branch -M main"
    ]
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"Executed: {cmd}")
        except Exception as e:
            print(f"Error {cmd}: {e}")

if __name__ == "__main__":
    run_git()
