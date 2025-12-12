#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# ///
"""Fork a new Terminal window with a specific command on macOS and Windows."""

import platform
import subprocess
import sys


def fork_terminal(command: str) -> str:
    """Open a new terminal window and execute the given command.

    Supports macOS (Terminal.app) and Windows (Windows Terminal or cmd.exe).
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        script = f'''
        tell application "Terminal"
            activate
            do script "{command.replace('"', '\\"')}"
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr

    elif system == "Windows":
        # Try Windows Terminal first (modern approach)
        try:
            result = subprocess.run(
                ["wt.exe", "new-tab", "--title", "Forked Terminal", "cmd", "/k", command],
                capture_output=True,
                text=True,
                check=True
            )
            return "Windows Terminal tab opened successfully"
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback to cmd.exe if Windows Terminal is not available
            result = subprocess.run(
                ["start", "cmd", "/k", command],
                shell=True,
                capture_output=True,
                text=True
            )
            return "Command Prompt window opened successfully" if result.returncode == 0 else result.stderr

    else:
        return f"Unsupported platform: {system}. Only macOS and Windows are supported."


if __name__ == "__main__":
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "echo 'Hello from forked terminal'"
    print(fork_terminal(cmd))
