# FoodExpiry/database/db_connection.py
from extensions import mongo

# Use the same DB from MONGO_URI (recommended)
foods_col = mongo.db.foods
users_col = mongo.db.users
