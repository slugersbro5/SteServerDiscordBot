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

        if self.is_running():

            self.bot.logger.warning(
                "Palworld server is already running."
            )

            return False

        exe = os.path.join(
            self.directory,
            self.executable,
        )

        if not os.path.exists(exe):

            raise FileNotFoundError(
                f"Palworld executable not found: {exe}"
            )

        self.bot.logger.info(
            f"Executable: {exe}"
        )

        self.bot.logger.info(
            f"Working directory: {self.directory}"
        )

        try:

            self.process = subprocess.Popen(
                [exe, "-log"],
                cwd=self.directory,
            )

            self.bot.logger.info(
                f"Palworld server started with PID: {self.process.pid}"
            )

            return True

        except Exception:

            self.bot.logger.exception(
                "Failed to start Palworld server."
            )

            raise

    def is_running(self):

        # First check the process this bot started.
        if self.process:

            if self.process.poll() is None:

                return True

            self.bot.logger.info(
                "Tracked Palworld process has exited."
            )

            self.process = None

        # If the bot restarted, search for an existing Palworld process.
        for process in psutil.process_iter(["pid", "name"]):

            try:

                name = process.info["name"] or ""

                if "palserver" in name.lower():

                    self.bot.logger.info(
                        f"Found existing Palworld process "
                        f"(PID: {process.pid})."
                    )

                    return True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):

                continue

        return False