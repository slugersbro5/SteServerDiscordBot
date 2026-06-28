import os
import subprocess
import psutil


class ProcessManager:

    def __init__(self, bot):

        self.bot = bot

        cfg = bot.config["palworld"]

        self.directory = cfg["directory"]
        self.executable = cfg["executable"]

        self.process = None

    async def start(self):

        exe = os.path.join(self.directory, self.executable
                           
                           )
        
        if not os.path.exists(exe):

            raise FileNotFoundError(exe)
        self.bot.logger.info(
            f"Starting Palworld server: {exe}")
        self.process = subprocess.Popen(
            [exe, "-log"],
            cwd=self.directory
        )

        self.bot.logger.info(
            f"Palworld server started with PID: {self.process.pid}"
        )
        return True
    def is_running(self):

    # 1. Check tracked PID first (most accurate)
        if hasattr(self, "pid") and self.pid:
            if psutil.pid_exists(self.pid):
             return True

    # 2. Check subprocess handle
        if self.process:
            return self.process.poll() is None

    # 3. Fallback scan
        for process in psutil.process_iter(["name"]):
            try:
                if "palserver" in (process.info["name"] or "").lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False