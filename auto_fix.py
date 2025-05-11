import subprocess

# Configure your project root directory
PROJECT_ROOT = "."

# Run black to format code according to line length (79)
def run_black():
    print("Running black...")
    subprocess.run(["black", PROJECT_ROOT, "--line-length", "79"])

# Run isort to sort and clean imports
def run_isort():
    print("Running isort...")
    subprocess.run(["isort", PROJECT_ROOT])

# Run autoflake to remove unused imports and variables (optional but useful)
def run_autoflake():
    print("Running autoflake...")
    subprocess.run([
        "autoflake",
        "--in-place",
        "--remove-unused-variables",
        "--remove-all-unused-imports",
        "--recursive",
        PROJECT_ROOT
    ])

# Main
if __name__ == "__main__":
    run_autoflake()
    run_isort()
    # skip black due to installation issues
    # run_black()
    print("✅ Auto-cleaning complete!") 