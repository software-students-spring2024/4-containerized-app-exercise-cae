"""
This module initializes the main Flask web app.
"""

import os
import logging
import sys
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import pika
from bson import ObjectId

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.config["UPLOAD_FOLDER"] = "uploads"

COUNTER = 0


def generate_filename():
    """This function generates unique file names for the temporarily stored images."""
    global COUNTER
    COUNTER += 1
    return f"image_{COUNTER}.jpg"


def get_mongo_client():
    """This function retrieves mongo client via mongo_uri."""
    mongo_uri = "mongodb://mongodb:27017/"
    # mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        raise ValueError("MongoDB URI not found in environment variables.")
    return MongoClient(mongo_uri)


def get_db(client):
    """This function retrieves main database for the program."""
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
    sys.exit(1)  # Fix for R1722


# Define routes and other Flask application logic below
@app.route("/")
def home():
    """This function renders the default index.html home page."""
    return render_template("index.html")


@app.route("/capture", methods=["POST"])
def capture():
    """This function handles image capture requests."""
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


COLOR_DATA = None


@app.route("/color_display")
def color_display():
    """This function renders color_display.html with color data retrieved from database."""
    return render_template("color_display.html", COLOR_DATA=COLOR_DATA)


def save_image_to_db(image_path):
    """This function saves the image data to the database."""
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        data = {"image_data": image_data}
        result = image_collection.insert_one(data)
        document_id = str(result.inserted_id)
        logging.debug("Image inserted into database with document ID: %s", document_id)
        return document_id
    except FileNotFoundError as file_not_found_error:
        logging.error(
            "Error inserting image into db: File not found - %s", file_not_found_error
        )
    except IOError as io_error:
        logging.error("Error inserting image into db: I/O error - %s", io_error)
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
    local_color_collection = db_client["Color"]

    document = local_color_collection.find_one({"_id": ObjectId(color_id)})
    if document:
        return document
    return None


def callback(channel, method, properties, body):
    """This function is called when a message is received from the queue."""
    color_id = body.decode()  # Decode the byte message to string
    print("Received message:", color_id)

    # Fetch image data from the database
    global COLOR_DATA
    COLOR_DATA = get_color_data_from_db(color_id)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
