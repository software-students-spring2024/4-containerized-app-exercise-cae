"""
This module initializes the ML client that will analyze the image captured by the user via app.py, 
extract its color palette, then store the palette data inside the database.
"""

import os
from pymongo import MongoClient
from cv2 import cv2
import numpy as np


def capture_image():
    """This function captures an image via the user's camera when called."""
    cap = cv2.VideoCapture(0)
    frame = cap.read()
    cap.release()
    return frame


def extract_color_palette(image):
    """This function extracts the average color palette of the captured image when called."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image_rgb.reshape(-1, 3)
    average_color = np.mean(pixels, axis=0)
    return average_color.tolist()


def store_color_data(color_data):
    """This function stores the color palette data into the database when called."""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("Error: MONGO_URI environment variable is not set.")
        return
    client = MongoClient(mongo_uri)
    db_client = client["CAE"]
    collection = db_client["CAE-Data"]
    collection.insert_one(color_data)


def main():
    """This is the main function of the client."""
    image = capture_image()
    color_palette = extract_color_palette(image)
    store_color_data({"color_palette": color_palette})


if __name__ == "__main__":
    main()
