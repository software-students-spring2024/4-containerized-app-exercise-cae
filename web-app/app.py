
#Module docstring goes here.
"""
This module initializes a Flask application and connects to a MongoDB database.
"""
import os
from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ConnectionError as MongoDBConnectionError

# Initialize Flask application
app = Flask(__name__)

def get_mongo_client():
    """
    Establishes a connection to MongoDB and returns a MongoClient object.
    """
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise ValueError("MongoDB URI not found in environment variables.")
    return MongoClient(mongo_uri)

# Connect to MongoDB
try:
    client = get_mongo_client()
    db = client.get_database()  # Replace with your database name if different
    print("Connected to MongoDB successfully.")
except MongoDBConnectionError as e:
    print("Error connecting to MongoDB:", e)
except ValueError as e:
    print("MongoDB URI not found:", e)

# Define routes and other Flask application logic below
