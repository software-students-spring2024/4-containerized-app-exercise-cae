"""
This module initializes the machine learning client.
"""

# pylint: disable=no-member
# pylint: disable=too-many-function-args
# pylint: disable=redefined-outer-name

import time
import cv2
import numpy as np
import webcolors
from pymongo import MongoClient
import pika
from bson import ObjectId


def rgb_to_hex(rgb):
    """This function transfers RBG values to HEX values."""
    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


def get_color_name(rgb):
    """This function use webcolors to try to get the name of the color."""
    try:
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        # Implement a way to find nearest color name if exact name not found
        return None


def extract_color_palette(image):
    """This function extracts the average color palette of the captured image when called."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = np.float32(image_rgb).reshape(-1, 3)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, _, palette = cv2.kmeans(pixels, 1, None, criteria, 10, flags)
    return palette[0]


def get_image_data_from_db(document_id):
    """This function retrieves image data from the MongoDB database."""
    # Connect to MongoDB and fetch image data
    mongo_uri = "mongodb://mongodb:27017/"
    # mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        raise EnvironmentError("MONGO_URI environment variable is not set.")
    client = MongoClient(mongo_uri)
    db_client = client["CAE"]
    image_collection = db_client["Image"]

    document = image_collection.find_one({"_id": ObjectId(document_id)})
    if document:
        return document.get("image_data")
    return None


def save_color_data_to_db(channel, color_data):
    """This function saves the color data to db."""
    # Connect to MongoDB
    mongo_uri = "mongodb://mongodb:27017/"
    # mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        raise EnvironmentError("MONGO_URI environment variable is not set.")
    client = MongoClient(mongo_uri)
    db_client = client["CAE"]
    color_collection = db_client["Color"]

    # Save color data to the database
    result = color_collection.insert_one(color_data)
    color_id = str(result.inserted_id)
    print(color_id)

    # Declare a queue for sending messages to main
    channel.queue_declare(queue="main")

    # Send the MongoDB ID back to main.py
    channel.basic_publish(exchange="", routing_key="main", body=color_id)

    print("Color data saved to the database")


def callback(channel, method, properties, body):  # pylint: disable=unused-argument
    """This function is called when a message is received from the queue."""
    document_id = body.decode()  # Decode the byte message to string
    print("Received message:", document_id)

    # Fetch image data from the database
    image_data = get_image_data_from_db(document_id)

    if image_data is None:
        print("Image data not found in the database")
        return

    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)
    color_palette = extract_color_palette(image)

    # RGB -> HEX conversion, get color name
    hex_color = rgb_to_hex(color_palette)
    color_name = get_color_name(color_palette) or "Unknown"

    color_data = {
        "rgb": list(map(int, color_palette)),
        "hex": hex_color,
        "name": color_name,
    }

    # Save color data to the database
    save_color_data_to_db(channel, color_data)


def establish_connection():
    """This function starts the RabbitMQ connection with main.py web app."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq")
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed. Retrying in 5 seconds...")
            time.sleep(5)


def main():
    """This function establishes connection with RabbitMQ and starts consuming messages."""
    connection = establish_connection()
    channel = connection.channel()

    # Declare a queue for receiving messages from main.py
    channel.queue_declare(queue="ml_client")

    # Define a callback function to process incoming messages
    channel.basic_consume(
        queue="ml_client", on_message_callback=callback, auto_ack=True
    )

    # Start consuming messages from the queue
    print("Waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
