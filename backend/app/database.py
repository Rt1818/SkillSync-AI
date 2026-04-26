from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

_client: AsyncIOMotorClient = None


async def connect_db() -> None:
    global _client
    import certifi
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        db = _client[settings.MONGODB_DB_NAME]
        # Test connection
        await _client.admin.command('ping')
        # TTL index: auto-delete sessions after 7 days
        await db.sessions.create_index("created_at", expireAfterSeconds=604800)
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"⚠️ MongoDB connection warning: {e}")
        # We don't raise here so the server can at least start and listen on the port
        # Render will see the port open and won't kill the container immediately


async def disconnect_db() -> None:
    global _client
    if _client:
        _client.close()
        print("🔌 Disconnected from MongoDB")


def get_db() -> AsyncIOMotorDatabase:
    return _client[settings.MONGODB_DB_NAME]
