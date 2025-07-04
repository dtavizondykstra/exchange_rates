#!/bin/zsh

# Source the .zshrc file to load environment variables and configurations
source ~/.zshrc

# Get the project directory (parent directory of the script directory)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Activate the virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Change to the project directory
cd "$PROJECT_DIR"

# Run the Python script
python3 main.py

# Deactivate the virtual environment
deactivate
