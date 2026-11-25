from pymongo import MongoClient
import os

# -------------------------
# Configuración / Conexión
# -------------------------
def get_mongo_client(uri: Optional[str] = None) -> MongoClient:
    uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(uri)

def get_collection_df(client: MongoClient, db_name: str, coll_name: str) -> pd.DataFrame:
    db = client[db_name]
    cursor = db[coll_name].find()
    df = pd.DataFrame(list(cursor))
    return df