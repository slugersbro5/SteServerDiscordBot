import asyncio
import subprocess

import aiohttp


class PalworldAPI:

    def __init__(self, bot):

        self.bot = bot

        cfg = bot.config["palworld"]

        self.base_url = (
            f"http://{cfg['host']}:{cfg['port']}/v1/api"
        )

        self.auth = aiohttp.BasicAuth(
            cfg["username"],
            cfg["password"]
        )

    async def _get(
        self,
        endpoint
    ):

        try:

            timeout = aiohttp.ClientTimeout(
                total=5
            )

            async with self.bot.http_session.get(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                timeout=timeout
            ) as response:

                response.raise_for_status()

                return await response.json()

        except aiohttp.ClientConnectorError:

            self.bot.logger.info(
                "Palworld server is offline."
            )

            return None

        except asyncio.TimeoutError:

            self.bot.logger.warning(
                "Palworld API timed out."
            )

            return None

        except Exception as e:

            self.bot.logger.error(
                f"Palworld API error: {e}"
            )

            return None

    async def _post(
        self,
        endpoint,
        payload=None
    ):

        try:

            timeout = aiohttp.ClientTimeout(
                total=5
            )

            async with self.bot.http_session.post(
                f"{self.base_url}/{endpoint}",
                auth=self.auth,
                json=payload,
                timeout=timeout
            ) as response:

                response.raise_for_status()

                if response.content_length:
                    return await response.json()

                return True

        except aiohttp.ClientConnectorError:

            self.bot.logger.info(
                "Palworld server is offline."
            )

            return None

        except asyncio.TimeoutError:

            self.bot.logger.warning(
                "Palworld API timed out."
            )

            return None

        except Exception as e:

            self.bot.logger.error(
                f"Palworld API error: {e}"
            )

            return None
        
    

    async def get_info(self):
        return await self._get("info")

    async def get_players(self):
        return await self._get("players")

    async def save_world(self):
        return await self._post("save")

    async def shutdown_server(
        self,
        wait_time=30,
        message="Server shutting down."
    ):

        return await self._post(
            "shutdown",
            {
                "waittime": wait_time,
                "message": message
            }
        )
    


    
    
    async def is_online(self):

        info = await self.get_info()

        return info is not None