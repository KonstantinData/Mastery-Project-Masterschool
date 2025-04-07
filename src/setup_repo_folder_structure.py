import os

# Define folders to be created
folders = [
    "data/bronze",
    "data/silver",
    "data/gold",
    "notebooks",
    "src",
    "sql/bronze",
    "sql/silver",
    "sql/gold",
    "outputs/figures",
    "outputs/tables",
    "outputs/models",
    "presentation",
]

# Folders that get a README.md
readme_folders = ["data", "sql", "src", "notebooks", "outputs", "presentation"]

# Create folders and add .gitkeep files
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, ".gitkeep"), "w") as f:
        pass  # create empty file

# Create empty __init__.py for src/
open("src/__init__.py", "a").close()

# Create README.md in selected folders
for folder in readme_folders:
    readme_path = os.path.join(folder, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(
                f"# {folder.capitalize()}\n\nThis folder contains files related to {folder}.\n"
            )

print("✅ Full TravelTide project structure created with .gitkeep and README.md files.")
