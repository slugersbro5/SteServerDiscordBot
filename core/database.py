import logging
import aiosqlite


class Database:

    def __init__(self, db_path="data/database.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("ServerBot")

    async def initialize(self):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    admin_role_id INTEGER,
                    log_channel_id INTEGER
                )
            """)

            await db.commit()

        self.logger.info("Database initialized.")

    async def set_admin_role(
        self,
        guild_id: int,
        role_id: int
    ):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
                INSERT INTO guild_settings
                (guild_id, admin_role_id)

                VALUES (?, ?)

                ON CONFLICT(guild_id)
                DO UPDATE SET
                admin_role_id = excluded.admin_role_id
            """, (guild_id, role_id))

            await db.commit()

    async def get_admin_role(
        self,
        guild_id: int
    ):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT admin_role_id
                FROM guild_settings
                WHERE guild_id = ?
            """, (guild_id,))

            row = await cursor.fetchone()

            return row[0] if row else None
        
    async def set_log_channel(
    self,
    guild_id: int,
    channel_id: int
):

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("""
            INSERT INTO guild_settings
            (guild_id, log_channel_id)

            VALUES (?, ?)

            ON CONFLICT(guild_id)
            DO UPDATE SET
            log_channel_id = excluded.log_channel_id
        """, (guild_id, channel_id))

            await db.commit()


    async def get_log_channel(
        self,
        guild_id: int
    ):

        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.execute("""
                SELECT log_channel_id
             FROM guild_settings
                WHERE guild_id = ?
            """, (guild_id,))

            row = await cursor.fetchone()

            return row[0] if row else None