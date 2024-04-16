"""
This module initializes the pytest test cases for main.py web app.
"""

import tempfile
from unittest.mock import patch, MagicMock
import pytest
from bson import ObjectId
from main import app, save_image_to_db, callback, image_collection
import main


@pytest.fixture
def test_client():
    """This function sets up a testing client."""
    app.config["TESTING"] = True
    test_client = app.test_client()

    # Setup: Create a temporary directory for file uploads
    with app.app_context():
        app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
    yield test_client


def test_home(test_client):
    """This function tests home page access."""
    response = test_client.get("/")
    assert b"Image Capture" in response.data


def test_capture_with_no_image_part():
    """This function tests the capture route without any images."""
    # Create a test client
    test_client = app.test_client()
    # Mock the request files object with no 'image' part
    mock_request = MagicMock(files={})
    with patch("main.request", mock_request):
        # Send a POST request to the /capture route
        response = test_client.post("/capture")
        # Assert that the request failed with status code 400
        assert response.status_code == 400
        # Assert that the response contains the expected error message
        assert b"No image part" in response.data


def test_capture_with_no_selected_file():
    """This function tests the capture route without any files."""
    # Create a test client
    test_client = app.test_client()
    # Mock the request files object with an empty filename
    mock_file_storage = MagicMock()
    mock_file_storage.filename = ""
    mock_request = MagicMock(files={"image": mock_file_storage})
    with patch("main.request", mock_request):
        # Send a POST request to the /capture route
        response = test_client.post("/capture")
        # Assert that the request failed with status code 400
        assert response.status_code == 400
        # Assert that the response contains the expected error message
        assert b"No selected file" in response.data


@pytest.fixture
def mock_mongo_client_fixture():
    """This function starts a mock mongo client for testing."""
    with patch("main.MongoClient") as mock_mongo_client:
        yield mock_mongo_client


@patch("main.MongoClient")
def test_get_color_data_from_db(mock_mongo_client_fixture):
    """This function tests if the program can get color data from db."""
    # Mock the MongoDB collection object
    mock_color_collection = MagicMock()
    mock_mongo_client_fixture.return_value.__getitem__.return_value.__getitem__.return_value = (
        mock_color_collection
    )
    # Set up a mock document to be returned by find_one
    mock_document = {
        "_id": ObjectId("605a698c80b5eaf424b1bb78"),
        "name": "Red",
        "rgb": "(255, 0, 0)",
        "hex": "#FF0000",
    }
    mock_color_collection.find_one.return_value = mock_document

    # Call the function with a mock color_id
    main.get_color_data_from_db("605a698c80b5eaf424b1bb78")

    # Assert that MongoClient was called
    assert mock_mongo_client_fixture.called


@pytest.fixture
def mock_image_file_content_fixture():
    """This function generates mock image file for testing."""
    return b"Fake image data"


def test_save_image_to_db(mock_image_file_content_fixture):
    """This function tests if the image could be saved to db."""
    image_path = "/path/to/image.jpg"
    document_id = "fake_document_id"

    # Mocking the open function to return fake image data
    with patch(
        "builtins.open",
        MagicMock(
            return_value=MagicMock(
                read=MagicMock(return_value=mock_image_file_content_fixture)
            )
        ),
    ):
        # Mocking the insert_one method of image_collection to return fake document ID
        with patch.object(
            image_collection,
            "insert_one",
            return_value=MagicMock(inserted_id=document_id),
        ):
            result = save_image_to_db(image_path)

    # Assert that the result is equal to the fake document ID
    assert result == document_id


def test_save_image_to_db_exception():
    """Test the previous function's exception handling."""
    # Mock image file path
    image_path = "/path/to/image.jpg"
    # Mock image file open context manager to raise an exception
    with patch("builtins.open", MagicMock(side_effect=Exception("Fake error"))):
        # Call save_image_to_db function and assert that it raises an exception
        with pytest.raises(Exception):
            save_image_to_db(image_path)


def test_callback_with_valid_color_id():
    """This function tests the callback function with a color id."""
    mock_body = MagicMock()
    mock_body.decode.return_value = "fake_color_id"
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_properties = MagicMock()
    with patch("main.get_color_data_from_db") as mock_get_color_data_from_db:
        callback(mock_channel, mock_method, mock_properties, mock_body)
        mock_body.decode.assert_called_once()
        mock_get_color_data_from_db.assert_called_once_with("fake_color_id")
