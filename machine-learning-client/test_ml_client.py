import cv2
import numpy as np
from unittest.mock import patch, MagicMock
import ml_client
from bson import ObjectId

def test_rgb_to_hex():
    rgb = (255, 0, 0)
    assert ml_client.rgb_to_hex(rgb) == "#ff0000"

def test_get_color_name():
    # Test with a known RGB value
    rgb = (255, 0, 0)
    assert ml_client.get_color_name(rgb) == "red"

    # Test with an unknown RGB value
    rgb = (100, 100, 100)
    assert ml_client.get_color_name(rgb) == None

@patch('ml_client.cv2.kmeans')
def test_extract_color_palette(mock_kmeans):
    mock_kmeans.return_value = (None, None, np.array([[255, 0, 0]], dtype=np.float32))
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    palette = ml_client.extract_color_palette(image)
    assert np.array_equal(palette, np.array([255, 0, 0], dtype=np.float32))

@patch('ml_client.MongoClient')
def test_get_image_data_from_db(mock_mongo_client):
    # Mock the MongoClient and its methods
    mock_image_collection = MagicMock()
    mock_db_client = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db_client
    mock_db_client.__getitem__.return_value = mock_image_collection

    # Mock the document to be returned by find_one
    mock_document = {"_id": ObjectId("605a698c80b5eaf424b1bb78"), "image_data": b'fake_image_data'}
    mock_image_collection.find_one.return_value = mock_document

    # Call get_image_data_from_db with a mock document_id
    image_data = ml_client.get_image_data_from_db("605a698c80b5eaf424b1bb78")

    # Assert that the MongoClient was called
    assert mock_mongo_client.called

@patch('ml_client.MongoClient')
def test_save_color_data_to_db(mock_mongo_client):
    mock_color_collection = MagicMock()
    mock_db_client = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_color_collection
    mock_color_collection.insert_one.return_value.inserted_id = 'some_color_id'
    mock_channel = MagicMock()
    ml_client.channel = mock_channel

    # Provide both arguments to the save_color_data_to_db function
    ml_client.save_color_data_to_db(mock_channel, {"rgb": [255, 0, 0], "hex": "#FF0000", "name": "red"})

    mock_channel.queue_declare.assert_called_once_with(queue='main')
    mock_channel.basic_publish.assert_called_once_with(exchange='', routing_key='main', body='some_color_id')

# Test case for the establish_connection function
def test_establish_connection():
    with patch('ml_client.pika.BlockingConnection') as mock_blocking_connection:
        mock_connection = MagicMock()
        mock_blocking_connection.return_value = mock_connection

        # Test connection establishment
        connection = ml_client.establish_connection()

        # Assert that BlockingConnection was called
        mock_blocking_connection.assert_called_once_with(ml_client.pika.ConnectionParameters(host="rabbitmq"))

        # Assert that the returned connection matches the mock connection
        assert connection == mock_connection

# Test case for the main function
@patch('ml_client.establish_connection')
def test_main(mock_establish_connection):
    # Create a mock connection and channel
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_establish_connection.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel

    # Call the main function
    ml_client.main()

    # Assert that establish_connection was called
    mock_establish_connection.assert_called_once()

    # Assert that start_consuming was called on the channel
    mock_channel.start_consuming.assert_called_once()

