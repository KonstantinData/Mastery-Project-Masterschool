import os

# Define folders to be created
folders = ["data/raw", "data/processed", "notebooks", "src", "visuals", "presentation"]

# Create folders and add a .gitkeep file
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, ".gitkeep"), "w") as f:
        pass  # create empty file

# Create __init__.py in src/ to mark it as a Python package
open("src/__init__.py", "a").close()

print("✅ Folder structure created with .gitkeep files.")
