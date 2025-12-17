import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Load env
load_dotenv()

uri = os.getenv("MONGO_URI")
print(f"DEBUG: MONGO_URI is {'Set' if uri else 'NOT SET'}")

if uri:
    # Mask password for display
    try:
        if "@" in uri:
            prefix, suffix = uri.split("@")
            print(f"DEBUG: Masked URI: {prefix.split('://')[0]}://****@{suffix}")
        else:
            print(f"DEBUG: URI (no password found): {uri}")
    except:
        print("DEBUG: Could not mask URI")

    print("\nAttempting connection to MongoDB...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Force a connection attempt
        client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB!")
    except Exception as e:
        print(f"ERROR: Could not connect to MongoDB. Reason: {e}")
else:
    print("ERROR: MONGO_URI missing in .env")
