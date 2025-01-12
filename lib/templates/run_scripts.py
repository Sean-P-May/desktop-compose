import os
import subprocess
from lib.config import Config

config = Config()

# Supported extensions and their commands
COMMANDS = {
    ".py": ["python"],
    ".ps1": ["powershell", "-File"],
    ".sh": ["bash"],
    ".js": ["node"]
}


def execute_script(file_path, arguments):
    """
    Executes a script file with the appropriate interpreter.

    Args:
        file_path (str): Path to the script file.
        arguments (list): List of additional arguments.
    """
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in COMMANDS:
        try:
            subprocess.run(COMMANDS[file_extension] + [file_path] + arguments, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Script {file_path} failed with exit code {e.returncode}")
    else:
        print(f"Unsupported file extension: {file_extension}")


def execute_shell_command(command):
    """
    Executes a shell command directly.

    Args:
        command (str): The shell command to execute.
    """
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Shell command failed with exit code {e.returncode}")


def resolve_and_execute(input_string):
    """
    Resolves the input string to a file, directory, or command and executes it.

    Args:
        input_string (str): Input string specifying a file, directory, or command.
    """
    parts = input_string.split()
    if not parts:
        print("No input provided.")
        return

    script_candidate = parts[0]
    arguments = parts[1:]

    # Normalize the scripts directory path
    scripts_directory = os.path.abspath(config.scripts_directory)
    script_path = os.path.join(scripts_directory, script_candidate)

    if os.path.isdir(script_path):  # It's a directory
        for file in os.listdir(script_path):
            file_name, file_extension = os.path.splitext(file)
            if file_name == script_candidate and file_extension in COMMANDS:
                execute_script(os.path.join(script_path, file), arguments)
                return
        print(f"No matching script found in directory: {script_path}")
    elif os.path.isfile(script_path):  # It's a file
        execute_script(script_path, arguments)
    else:  # Treat as a shell command
        execute_shell_command(" ".join([script_candidate] + arguments))