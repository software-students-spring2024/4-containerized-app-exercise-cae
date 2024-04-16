"""
This module initializes a Flask application and connects to a MongoDB database.
"""

from flask import Flask, request, jsonify, render_template
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pika
import logging
from bson import ObjectId

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.config["UPLOAD_FOLDER"] = "uploads"

counter = 0


def generate_filename():
    global counter
    counter += 1
    return f"image_{counter}.jpg"


# Initialize the MongoDB client
def get_mongo_client():
    mongo_uri = "mongodb://mongodb:27017/"
    # mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        raise ValueError("MongoDB URI not found in environment variables.")
    return MongoClient(mongo_uri)


# Function to get the database
def get_db(client):
    db_name = "CAE"
    return client[db_name]


# Connect to MongoDB
try:
    mongo_client = get_mongo_client()
    db = get_db(mongo_client)
    image_collection = db["Image"]
    color_collection = db["Color"]
    print("Connected to MongoDB successfully.")
except ConnectionError as e:
    print("Error connecting to MongoDB:", e)
    exit(1)


# Define routes and other Flask application logic below
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/capture", methods=["POST"])
def capture():
    if "image" not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Generate a filename
    filename = generate_filename()
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    print(image_path)

    # Save the image to the uploads folder
    file.save(image_path)

    # Save image filename to database
    document_id = save_image_to_db(image_path)

    # Initialize the message broker connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Declare a queue for sending messages to ml_client.py
    channel.queue_declare(queue="main")

    # Declare a queue for receiving messages from ml_client.py
    channel.queue_declare(queue="ml_client")

    # Publish a message to the message broker
    channel.basic_publish(exchange="", routing_key="ml_client", body=document_id)

    # Define a callback function to process incoming messages
    channel.basic_consume(queue="main", on_message_callback=callback, auto_ack=True)

    # Start consuming messages from the queue
    print("Waiting for messages...")
    channel.start_consuming()

    return (
        jsonify(
            message="Image saved to database and analysis triggered",
            document_id=document_id,
        ),
        201,
    )


color_data = None


@app.route("/color_display")
def color_display():
    if color_data is None:
        return render_template("color_display.html", color_data=None)
    else:
        return render_template("color_display.html", color_data=color_data)


logging.basicConfig(level=logging.DEBUG)


def save_image_to_db(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        data = {"image_data": image_data}
        result = image_collection.insert_one(data)
        document_id = str(result.inserted_id)
        logging.debug(f"Image inserted into database with document ID: {document_id}")
        return str(result.inserted_id)
    except Exception as e:
        logging.error(f"Error inserting image into database: {e}")
        return None


def get_color_data_from_db(color_id):
    """This function retrieves color data from the MongoDB database."""
    # Connect to MongoDB and fetch image data
    mongo_uri = "mongodb://mongodb:27017/"
    # mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        raise EnvironmentError("MONGO_URI environment variable is not set.")
    client = MongoClient(mongo_uri)
    db_client = client["CAE"]
    color_collection = db_client["Color"]

    document = color_collection.find_one({"_id": ObjectId(color_id)})
    if document:
        return document
    return None


def callback(ch, method, properties, body):
    """This function is called when a message is received from the queue."""
    global color_data
    color_id = body.decode()  # Decode the byte message to string
    print("Received message:", color_id)

    # Fetch image data from the database
    color_data = get_color_data_from_db(color_id)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
