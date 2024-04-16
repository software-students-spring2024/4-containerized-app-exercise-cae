import os
import tempfile
import pytest
from main import app, get_color_data_from_db, save_image_to_db, callback
from unittest.mock import patch, MagicMock
from bson import ObjectId
import main

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    # Setup: Create a temporary directory for file uploads
    with app.app_context():
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    yield client

def test_home(client):
    response = client.get('/')
    assert b'Image Capture' in response.data

def test_capture_with_no_image_part():
    # Create a test client
    client = app.test_client()
    # Mock the request files object with no 'image' part
    mock_request = MagicMock(files={})
    with patch('main.request', mock_request):
        # Send a POST request to the /capture route
        response = client.post('/capture')
        # Assert that the request failed with status code 400
        assert response.status_code == 400
        # Assert that the response contains the expected error message
        assert b'No image part' in response.data

def test_capture_with_no_selected_file():
    # Create a test client
    client = app.test_client()
    # Mock the request files object with an empty filename
    mock_file_storage = MagicMock()
    mock_file_storage.filename = ''
    mock_request = MagicMock(files={'image': mock_file_storage})
    with patch('main.request', mock_request):
        # Send a POST request to the /capture route
        response = client.post('/capture')
        # Assert that the request failed with status code 400
        assert response.status_code == 400
        # Assert that the response contains the expected error message
        assert b'No selected file' in response.data

@patch('main.color_data', {"name": "Red", "rgb": "(255, 0, 0)", "hex": "#FF0000"})
def test_color_display(client):
    response = client.get('/color_display')
    assert b'Detected Color Information' in response.data
    assert b'Red' in response.data

@pytest.fixture
def mock_mongo_client():
    with patch('main.MongoClient') as mock_mongo_client:
        yield mock_mongo_client

@patch('main.MongoClient')
def test_get_color_data_from_db(mock_mongo_client):
    # Mock the MongoDB collection object
    mock_color_collection = MagicMock()
    mock_db_client = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value.__getitem__.return_value = mock_color_collection
    # Set up a mock document to be returned by find_one
    mock_document = {"_id": ObjectId("605a698c80b5eaf424b1bb78"), "name": "Red", "rgb": "(255, 0, 0)", "hex": "#FF0000"}
    mock_color_collection.find_one.return_value = mock_document

    # Call the function with a mock color_id
    color_data = main.get_color_data_from_db("605a698c80b5eaf424b1bb78")

    # Assert that MongoClient was called
    assert mock_mongo_client.called

# Fixture for mocking the image file content
@pytest.fixture
def mock_image_file_content():
    return b'Fake image data'

def test_save_image_to_db_exception(mock_image_file_content):
    # Mock image file path
    image_path = '/path/to/image.jpg'
    # Mock image file open context manager to raise an exception
    with patch('builtins.open', MagicMock(side_effect=Exception('Fake error'))) as mock_open:
        # Call save_image_to_db function
        document_id = save_image_to_db(image_path)
        # Assert that image file is opened with correct path
        mock_open.assert_called_once_with(image_path, 'rb')
        # Assert that None is returned when an exception occurs
        assert document_id is None

def test_callback_with_valid_color_id():
    # Mock the body of the message
    mock_body = MagicMock()
    mock_body.decode.return_value = 'fake_color_id'
    # Mock the get_color_data_from_db function
    with patch('main.get_color_data_from_db') as mock_get_color_data_from_db:
        # Call the callback function
        callback(None, None, None, mock_body)
        # Assert that the color_id was correctly decoded from the message body
        mock_body.decode.assert_called_once()
        # Assert that get_color_data_from_db was called with the correct color_id
        mock_get_color_data_from_db.assert_called_once_with('fake_color_id')


