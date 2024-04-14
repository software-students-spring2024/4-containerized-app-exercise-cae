import cv2
import pymongo
import numpy as np 

class mlClient:
    def __init__(self, db_url, db_name):
        self.db_client = pymongo.MongoClient(db_url)
        self.db = self.db_client[db_name]

    def capture_color(self):
        # captures frames from camera, processes them, detects colors using 'detect_color' method, and saves color information to database using 'save_color'

    def detect_color(self, frame):
        # implement color detection algo, we can calculate the average color of a captured frame

        # calculate avg color
        avg_color_per_row = np.average(frame, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)

        return avg_color
    
    def save_color(self, color):
        color_data = {
            'red': color[0],
            'green': color[1],
            'blue': color[2]
        }
        self.db.colors.insert_one(color_data)

if __name__ == "__main__":
    # configure db_url, db_name
    # initialize ML client and capture color from camera