from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://zc1545:200893356azxsd@cluster0.fy1j2yw.mongodb.net/CAE')

db = client['CAE']