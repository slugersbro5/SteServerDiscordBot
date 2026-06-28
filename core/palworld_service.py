class PalworldService:
    def __init__(self, api, process_manager):
        self.api = api
        self.process_manager = process_manager
        async def start(self):
            return await self.process_manager.start()
        async def save(self):
            return await self.api.save_server()
        async def shutdown(self,
                           wait_time,
                           message
                           ):
            return await self.api.shutdown_server(
                wait_time,
                message
            )
        async def get_players(self):
            return await self.api.get_players()