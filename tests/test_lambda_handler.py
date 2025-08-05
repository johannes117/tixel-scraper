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
def mock_dynamodb_table(mocker):
    """Mocks the DynamoDB table resource."""
    mock_table = MagicMock()
    # Use a dictionary to simulate the DynamoDB table's state
    db_state = {}

    def get_item_side_effect(Key):
        item_id = Key['id']
        if item_id in db_state:
            return {'Item': db_state[item_id]}
        return {}

    def put_item_side_effect(Item):
        db_state[Item['id']] = Item

    mock_table.get_item.side_effect = get_item_side_effect
    mock_table.put_item.side_effect = put_item_side_effect

    mocker.patch('boto3.resource').return_value.Table.return_value = mock_table
    return mock_table

def test_tickets_found_first_time(mocker, mock_dynamodb_table, mock_lambda_context):
    """
    Tests the scenario where a matching ticket is found for the first time.
    """
    # Arrange: Mock external calls
    mock_check_tickets = mocker.patch('src.lambda_function.check_tickets', return_value=(True, {"type": "GA", "price": "90.00", "quantity": 2}))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    # Start with a state where notification has not been sent
    mock_dynamodb_table.get_item.return_value = {'Item': {'notification_sent': False}}

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
    mock_dynamodb_table.put_item.assert_called_with(Item={'id': 'notification_state', 'notification_sent': True})

def test_tickets_not_found(mocker, mock_dynamodb_table, mock_lambda_context):
    """
    Tests the scenario where no matching tickets are found.
    """
    # Arrange
    mock_check_tickets = mocker.patch('src.lambda_function.check_tickets', return_value=(False, None))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    mock_dynamodb_table.get_item.return_value = {'Item': {'notification_sent': False}}

    # Act
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert body['matching_ticket_found'] is False
    
    mock_check_tickets.assert_called_once()
    mock_send_email.assert_not_called()
    mock_dynamodb_table.put_item.assert_not_called() # State should not change

def test_tickets_found_but_already_notified(mocker, mock_dynamodb_table, mock_lambda_context):
    """
    Tests that no new email is sent if a notification was already sent.
    """
    # Arrange
    mocker.patch('src.lambda_function.check_tickets', return_value=(True, {"type": "GA", "price": "90.00", "quantity": 2}))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    # Start with a state where notification HAS been sent
    mock_dynamodb_table.get_item.return_value = {'Item': {'notification_sent': True}}

    # Act
    result = lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    assert result['statusCode'] == 200
    assert json.loads(result['body'])['matching_ticket_found'] is True
    
    mock_send_email.assert_not_called()
    mock_dynamodb_table.put_item.assert_not_called()

def test_tickets_gone_resets_state(mocker, mock_dynamodb_table, mock_lambda_context):
    """
    Tests that the notification state is reset when tickets are no longer available.
    """
    # Arrange
    mocker.patch('src.lambda_function.check_tickets', return_value=(False, None))
    mock_send_email = mocker.patch('src.lambda_function.send_email')
    # Start with a state where notification HAS been sent
    mock_dynamodb_table.get_item.return_value = {'Item': {'notification_sent': True}}

    # Act
    lambda_function.lambda_handler({}, mock_lambda_context)

    # Assert
    mock_send_email.assert_not_called()
    # Assert that the state was reset to False
    mock_dynamodb_table.put_item.assert_called_with(Item={'id': 'notification_state', 'notification_sent': False})