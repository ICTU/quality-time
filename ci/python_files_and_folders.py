"""Determine the Python files and folders in the current directory."""

from pathlib import Path

def python_files_and_folders() -> list[str]:
    """Return the Python files and folders in the current directory."""
    python_files = [python_file.name for python_file in Path(".").glob('*.py') if not python_file.name.startswith(".")]
    python_folders = [folder_name for folder_name in ("src", "tests") if Path(folder_name).exists()]
    return python_files + python_folders


if __name__ == "__main__":
    print(" ".join(python_files_and_folders()))
