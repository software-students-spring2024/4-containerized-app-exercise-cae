"""
This module initializes the pytest test cases for ml_client.py client.
"""

from unittest.mock import patch, MagicMock
import numpy as np
from bson import ObjectId
import ml_client

def test_rgb_to_hex():
    """This function tests RBB to HEX function."""
    rgb = (255, 0, 0)
    assert ml_client.rgb_to_hex(rgb) == "#ff0000"

def test_get_color_name():
    """This function tests get color name function"""
    rgb = (255, 0, 0)
    assert ml_client.get_color_name(rgb) == "red"

    rgb = (100, 100, 100)
    assert ml_client.get_color_name(rgb) is None

@patch('ml_client.cv2.kmeans')
def test_extract_color_palette(mock_kmeans):
    """This function tests extract color palette function."""
    mock_kmeans.return_value = (None, None, np.array([[255, 0, 0]], dtype=np.float32))
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    palette = ml_client.extract_color_palette(image)
    assert np.array_equal(palette, np.array([255, 0, 0], dtype=np.float32))

@patch('ml_client.MongoClient')
def test_get_image_data_from_db(mock_mongo_client):
    """This function tests get image data from db function."""
    # Mock the MongoClient and its methods
    mock_image_collection = MagicMock()
    mock_db_client = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db_client
    mock_db_client.__getitem__.return_value = mock_image_collection

    # Mock the document to be returned by find_one
    mock_document = {"_id": ObjectId("605a698c80b5eaf424b1bb78"), "image_data": b'fake_image_data'}
    mock_image_collection.find_one.return_value = mock_document

    # Call get_image_data_from_db with a mock document_id
    ml_client.get_image_data_from_db("605a698c80b5eaf424b1bb78")

    # Assert that the MongoClient was called
    assert mock_mongo_client.called

@patch('ml_client.MongoClient')
def test_save_color_data_to_db(mock_mongo_client):
    """This function tests save color data to db function."""
    mock_cc = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_cc
    mock_cc.insert_one.return_value.inserted_id = 'some_color_id'
    cha = MagicMock()
    ml_client.channel = cha

    # Provide both arguments to the save_color_data_to_db function
    ml_client.save_color_data_to_db(cha, {"rgb": [255, 0, 0], "hex": "#FF0000", "name": "red"})

    cha.queue_declare.assert_called_once_with(queue='main')
    cha.basic_publish.assert_called_once_with(exchange='', routing_key='main', body='some_color_id')

# Test case for the establish_connection function
def test_establish_connection():
    """This function tests establish connection function."""
    with patch('ml_client.pika.BlockingConnection') as mock_bc:
        mock_connection = MagicMock()
        mock_bc.return_value = mock_connection

        # Test connection establishment
        connection = ml_client.establish_connection()

        # Assert that BlockingConnection was called
        mock_bc.assert_called_once_with(ml_client.pika.ConnectionParameters(host="rabbitmq"))

        # Assert that the returned connection matches the mock connection
        assert connection == mock_connection

# Test case for the main function
@patch('ml_client.establish_connection')
def test_main(mock_establish_connection):
    """This function sets up a mock connection for testing."""
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
