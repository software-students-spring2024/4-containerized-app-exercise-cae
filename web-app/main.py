#Module docstring goes here.
"""
This module initializes a Flask application and connects to a MongoDB database.
"""
from ml_client.ml_client import analyze_image # this function must be updated accordingly in ml_client.py
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from bson.json_util import dumps
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

# Initialize Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

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
    db_name = os.getenv("MONGO_DB_NAME", "CAE")
    return client[db_name]

# Connect to MongoDB
try:
    client = get_mongo_client()
    db = get_db(client)
    collection_name = "CAE-Data"
    collection = db[collection_name]
    print("Connected to MongoDB successfully.")
except ConnectionError as e:
    print("Error connecting to MongoDB:", e)
    exit(1)

# Define routes and other Flask application logic below
@app.route('/')
def home():
    return render_template('index.html')

# Route to upload image to db
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # secure filename and save in uploads folder
    filename = secure_filename(file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)

    # call analyze_image function from ml_client.py
    color_data = analyze_image(image_path)

    # remove image after analysis if not required to keep
    os.remove(image_path)

    # insert color data into db
    db.collection_name.insert_one(color_data)

    return jsonify(color_data), 201

# Route to add new color data
@app.route('/color', methods=['POST'])
def add_color_data():
    try:
        color_data = request.json
        result = db.collection_name.insert_one(color_data)
        return jsonify(message="Color data added", id=str(result.inserted_id)), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

# Route to retrieve all color data
@app.route('/colors', methods=['GET'])
def get_all_colors():
    try:
        colors = list(db.collection_name.find({}, {'_id': 0}))
        return dumps(colors), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

# Route to retrieve a specific color by name
@app.route('/color/<name>', methods=['GET'])
def get_color_by_name(name):
    try:
        color = db.collection_name.find_one({'name': name}, {'_id: 0'})
        if color:
            return dumps(color), 200
        else:
            return jsonify(message="Color not found"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
