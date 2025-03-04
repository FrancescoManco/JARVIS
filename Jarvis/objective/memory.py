from pymongo import MongoClient

class MongoDBHandler:
    def __init__(self, connection_string: str, db_name: str, collection_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_message(self, message: dict):
        """Insert a message into the collection."""
        self.collection.insert_one(message)

    def get_all_messages(self):
        """Retrieve all messages from the collection."""
        return list(self.collection.find({}))
    

    def clear_messages(self):
        """Clear all messages in the collection."""
        self.collection.delete_many({})
