class PalworldService:

    def __init__(self, api, process):
        self.api = api
        self.process = process

    # process control
    async def start(self):
        return await self.process.start()

    async def is_running(self):
        return self.process.is_running()

    # API passthroughs
    async def get_info(self):
        return await self.api.get_info()

    async def get_players(self):
        return await self.api.get_players()

    async def save(self):
        return await self.api.save_world()

    async def shutdown(self, wait_time=30, message="Server shutting down"):
        return await self.api.shutdown_server(wait_time, message)