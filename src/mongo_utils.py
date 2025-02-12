import os
import pymongo

# Load MongoDB URI from environment or hardcode for now
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://morse_admin:cc51HtU5YxOEFyxn@morsecluster.dyq7j.mongodb.net/?retryWrites=true&w=majority&appName=MorseCluster")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["morse_code_db"]
test_sets_collection = db["test_sets"]

def fetch_test_sets():
    """Fetch all test sets from MongoDB."""
    test_sets = {}
    for doc in test_sets_collection.find():
        test_sets[doc["name"]] = doc["words"]  # Use 'name' as key instead of '_id'
    return test_sets

def insert_test_set(name, words):
    """Insert a new test set into MongoDB."""
    test_sets_collection.insert_one({"name": name, "words": words})
    return f"Test set '{name}' added successfully!"

def delete_test_set(name):
    """Delete a test set from MongoDB."""
    test_sets_collection.delete_one({"name": name})
    return f"Test set '{name}' deleted."
