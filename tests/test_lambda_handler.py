# tests/test_lambda_handler.py

import os
import json
import pytest
from unittest.mock import MagicMock

# Set environment variables before importing the lambda function
os.environ['DYNAMODB_TABLE_NAME'] = 'mock-table'
os.environ['RESEND_API_KEY'] = 'mock-key'
os.environ['FROM_ADDRESS'] = 'test@example.com'
os.environ['TO_ADDRESSES'] = 'recipient@example.com'
os.environ['TIXEL_URL'] = 'https://tixel.com/test'
os.environ['MAX_PRICE'] = '100'
os.environ['DESIRED_QUANTITY'] = '2'

from src import lambda_function

@pytest.fixture
def mock_lambda_context():
    """Mocks the Lambda context object."""
    context = MagicMock()
    context.function_name = "test-tixel-scraper"
    context.aws_request_id = "test-request-id"
    return context

@pytest.fixture
def mock_table(mocker):
    """
    Mocks the DynamoDB table object by patching it directly in the
    lambda_function module where it's used. This is the correct way to mock it.
    """
    mocked_table = mocker.patch('src.lambda_function.table')
    return mocked_table

@pytest.fixture(autouse=True)
def mock_email_template(mocker):
    """
    Mocks the file reading for the email template for all tests.
    This prevents the FileNotFoundError and makes tests independent of the file system.
    """
    mocker.patch('src.lambda_function.get_email_template', return_value="<html>Mock Email</html>")


def test_tickets_found_first_time(mocker, mock_table, mock_lambda_context):
    """
    Tests the scenario where a matching ticket is found for the first time.
    """
    # Arrange: Mock external calls
    mock_check_tickets = mocker.patch('src.lambda_function.check_tickets', return_value=(True, {"type": "GA", "price": "90.00", "quantity": 2}))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    
    # Configure the DynamoDB mock to return a state where notification has not been sent
    mock_table.get_item.return_value = {'Item': {'id': 'notification_state', 'notification_sent': False}}

    # Act: Run the handler
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert: Verify the outcomes
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['matching_ticket_found'] is True
    
    # Assert that key functions were called
    mock_check_tickets.assert_called_once()
    mock_send_email.assert_called_once()
    # Assert that the state was updated to True
    mock_table.put_item.assert_called_with(Item={'id': 'notification_state', 'notification_sent': True})

def test_tickets_not_found(mocker, mock_table, mock_lambda_context):
    """
    Tests the scenario where no matching tickets are found.
    """
    # Arrange
    mock_check_tickets = mocker.patch('src.lambda_function.check_tickets', return_value=(False, None))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    mock_table.get_item.return_value = {'Item': {'id': 'notification_state', 'notification_sent': False}}

    # Act
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['matching_ticket_found'] is False
    
    mock_check_tickets.assert_called_once()
    mock_send_email.assert_not_called()
    mock_table.put_item.assert_not_called() # State should not change

def test_tickets_found_but_already_notified(mocker, mock_table, mock_lambda_context):
    """
    Tests that no new email is sent if a notification was already sent.
    """
    # Arrange
    mocker.patch('src.lambda_function.check_tickets', return_value=(True, {"type": "GA", "price": "90.00", "quantity": 2}))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    
    # Configure the DynamoDB mock to return a state where notification HAS been sent
    mock_table.get_item.return_value = {'Item': {'id': 'notification_state', 'notification_sent': True}}

    # Act
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    assert result['statusCode'] == 200
    assert json.loads(result['body'])['matching_ticket_found'] is True
    
    mock_send_email.assert_not_called()
    mock_table.put_item.assert_not_called()

def test_tickets_gone_resets_state(mocker, mock_table, mock_lambda_context):
    """
    Tests that the notification state is reset when tickets are no longer available.
    """
    # Arrange
    mocker.patch('src.lambda_function.check_tickets', return_value=(False, None))
    mock_send_email = mocker.patch('src.lambda_function.send_email')

    # Configure the DynamoDB mock to return a state where notification HAS been sent
    mock_table.get_item.return_value = {'Item': {'id': 'notification_state', 'notification_sent': True}}

    # Act
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    assert result['statusCode'] == 200
    mock_send_email.assert_not_called()

    # Assert that the state was reset to False
    mock_table.put_item.assert_called_with(Item={'id': 'notification_state', 'notification_sent': False})