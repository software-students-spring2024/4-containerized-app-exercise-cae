#Module docstring goes here.
"""
This module initializes a Flask application and connects to a MongoDB database.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps

load_dotenv()

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

    # mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ml_data")
    # return MongoClient(mongo_uri)

# Function to get the database
def get_db(client):
    db_name = os.getenv("MONGO_DB_NAME", "ml_data")
    return client[db_name]

# Connect to MongoDB
try:
    client = get_mongo_client()
    db = get_db(client)
    print("Connected to MongoDB successfully.")
except ConnectionError as e:
    print("Error connecting to MongoDB:", e)
    exit(1)

# Define routes and other Flask application logic below
@app.route('/')
def home():
    return "Welcome to the ML Color Detection App!"

# Route to add new color data
@app.route('/color', methods=['POST'])
def add_color_data():
    try:
        color_data = request.json
        result = db.colors.insert_one(color_data)
        return jsonify(message="Color data added", id=str(result.inserted_id)), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

# Route to retrieve all color data
@app.route('/colors', methods=['GET'])
def get_all_colors():
    try:
        colors = list(db.colors.find({}, {'_id': 0}))
        return dumps(colors), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

# Route to retrieve a specific color by name
@app.route('/color/<name>', methods=['GET'])
def get_color_by_name(name):
    try:
        color = db.colors.find_one({'name': name}, {'_id: 0'})
        if color:
            return dumps(color), 200
        else:
            return jsonify(message="Color not found"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
