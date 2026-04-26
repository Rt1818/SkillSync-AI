from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

_client: AsyncIOMotorClient = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = _client[settings.MONGODB_DB_NAME]
    # TTL index: auto-delete sessions after 7 days
    await db.sessions.create_index("created_at", expireAfterSeconds=604800)
    print("✅ Connected to MongoDB")


async def disconnect_db() -> None:
    global _client
    if _client:
        _client.close()
        print("🔌 Disconnected from MongoDB")


def get_db() -> AsyncIOMotorDatabase:
    return _client[settings.MONGODB_DB_NAME]
