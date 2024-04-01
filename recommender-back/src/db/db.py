import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
if 'MONGO_URI' in os.environ:
    mongo_uri = os.environ['MONGO_URI']
else:
    mongo_uri = os.environ.get('DEVELOPMENT_DB_URI')
print(' * Connecting to MongoDB')


def get_db():
    """
    Connects to the MongoDB and returns the 'poidata' database.

    Returns:
        pymongo.database.Database or None: The MongoDB database instance, or None if connection fails.
    """
    try:
        client = MongoClient(mongo_uri)
        return client.get_database('poidata')
    except Exception as error:
        print(' * Error connecting to MongoDB:', error)
        return None


def read_POIs():
    file = open(os.path.join(os.path.dirname(__file__), '..', 'static', 'pois_db.txt'), 'r')
    pois = []
    for line in file:
        parsed_obj = json.loads(line)
        pois.append(parsed_obj)
    file.close()
    return pois

def get_collection():
    """
    Retrieves the 'pois' collection from the MongoDB database.

    Returns:
        pymongo.collection.Collection or None: The MongoDB collection instance, or None if retrieval fails.
    """
    try:
        db = get_db()
        return db['pois']
    except Exception as error:
        print(' * Error getting collection in MongoDB:', error)
        return None
