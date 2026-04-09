import os

def check():
    with open("size.txt", "w") as f:
        try:
            f.write(f"Size: {os.path.getsize('frontend/dashboard.png')}")
        except Exception as e:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    check()
