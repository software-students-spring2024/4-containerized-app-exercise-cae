"""
This module initializes the ML client that will analyze the image captured by the user via app.py, 
extract its color palette, then store the palette data inside the database.
"""

import os
import cv2
import numpy as np
import webcolors
from pymongo import MongoClient


def capture_image():
    """This function captures an image via the user's camera when called."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise ValueError("Could not capture the image.")
    return frame 

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color_name(rgb):
    try:
        return webcolors.rgb_to_name(rgb)
    except ValueError:
        # Implement a way to find nearest color name if exact name not found
        return None

def extract_color_palette(image):
    """This function extracts the average color palette of the captured image when called."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # pixels = image_rgb.reshape(-1, 3)
    # average_color = np.mean(pixels, axis=0)
    # return average_color.tolist()
    pixels = np.float32(image_rgb).reshape(-1, 3)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, 1, None, criteria, 10, flags)
    return palette[0]

# Added method to process image file and return color data
def analyze_image(image_path):
    # image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
    # color_palette = extract_color_palette(image)
    # enhance functionality later to include name, RGB, and HEX values
    # color_data = {"color_palette": color_palette}
    # store_color_data(color_data)
    # return color_data

    # Read & decode img
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

    # Extract color palette (avg color)
    color_palette = extract_color_palette(image)

    # RGB -> HEX conversion, get color name
    hex_color = rgb_to_hex(color_palette)
    color_name = get_color_name(color_palette) or "Unknown"

    color_data = {
        "rgb": list(map(int, color_palette)),
        "hex": hex_color,
        "name": color_name
    }
    return color_data

def store_color_data(color_data):
    """This function stores the color palette data into the database when called."""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        # print("Error: MONGO_URI environment variable is not set.")
        # return
        raise EnvironmentError("MONGO_URI environment variable is not set.")
    client = MongoClient(mongo_uri)
    db_client = client["CAE"]
    collection = db_client["CAE-Data"]
    collection.insert_one(color_data)


# def main():
    """This is the main function of the client."""
    # image = capture_image()
    # color_palette = extract_color_palette(image)
    # store_color_data({"color_palette": color_palette})


# if __name__ == "__main__":
    # main()
