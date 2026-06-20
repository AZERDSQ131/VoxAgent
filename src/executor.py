import subprocess
import shlex
import os

from config import BASH_TIMEOUT

ALLOWED_COMMANDS = [
    "ls", "cat", "echo", "pwd", "cd", "mkdir", "touch", "cp", "mv", "rm",
    "grep", "find", "head", "tail", "wc", "sort", "uniq", "cut", "tr",
    "python3", "python", "node", "npm", "npx", "pip3", "pip",
    "git", "curl", "wget", "tar", "gzip", "gunzip", "unzip",
    "chmod", "chown", "date", "whoami", "id", "uname", "df", "du",
    "ps", "kill", "top", "env", "which", "file", "stat",
    "mkdir", "rmdir", "ln",
]

DANGEROUS_PATTERNS = [
    "rm -rf /", "rm -rf ~", "rm -rf .", "mkfs", "dd if=",
    ":(){ :|:& };:", "wget -O - | sh", "curl.*|.*sh",
    "sudo", "su ", "passwd", "> /dev/", "chmod 777 /",
    "chown .* /", "mv.*/.*/", "> /etc/",
]


class Executor:
    def __init__(self, cwd=None):
        self.cwd = cwd or os.getcwd()

    def is_safe(self, command):
        cmd_lower = command.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return False, f"Commande bloquee (pattern dangereux: {pattern})"
        cmd_base = shlex.split(command)[0] if shlex.split(command) else ""
        if cmd_base and cmd_base not in ALLOWED_COMMANDS:
            return False, f"Commande non autorisee: {cmd_base}"
        return True, None

    def execute(self, command):
        safe, reason = self.is_safe(command)
        if not safe:
            return f"ERREUR: {reason}"
        try:
            result = subprocess.run(
                ["bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=BASH_TIMEOUT,
                cwd=self.cwd,
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if error:
                output = f"{output}\n[stderr] {error}" if output else f"[stderr] {error}"
            if result.returncode != 0:
                output = f"Exit code {result.returncode}\n{output}" if output else f"Exit code {result.returncode}"
            return output or "(aucun output)"
        except subprocess.TimeoutExpired:
            return f"ERREUR: timeout depasse ({BASH_TIMEOUT}s)"
        except Exception as e:
            return f"ERREUR: {e}"
