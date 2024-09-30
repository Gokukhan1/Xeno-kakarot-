from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

BDB_URI = "mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority"

mongo = MongoClient(BDB_URI)
dbname = mongo.hasnainkkDb
