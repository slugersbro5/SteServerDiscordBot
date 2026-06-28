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
    async def is_running(self):

        if self.process:

            return self.process.poll() is None
        for process in psutil.process_iter(["name"]):

            if process.info["name"] == "PalServer.exe":

                return True
        return False