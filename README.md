# Tixel Ticket Scraper (Serverless AWS Version)

A cost-effective, serverless application that runs on AWS to automatically monitor ticket availability on Tixel. It sends you an email notification the moment tickets matching your specific criteria (price and quantity) are found.

## How It Works (Architecture)

This solution is built on a serverless AWS architecture, which is highly efficient and cost-effective.

- **AWS Lambda**: Executes the Python scraping code on a schedule without needing a dedicated server.
- **Amazon EventBridge Scheduler**: Triggers the Lambda function at a defined interval (e.g., every minute).
- **Amazon DynamoDB**: Stores the notification state to prevent sending duplicate emails for the same ticket listing.
- **AWS CloudFormation**: Defines and deploys all the necessary AWS resources in a single, manageable stack.
- **Amazon S3**: Stores the Lambda function's deployment package.
- **Amazon CloudWatch**: Collects logs for monitoring and debugging.
- **Resend API**: Used to send email notifications.

This setup typically falls within the **AWS Free Tier**, making it virtually free to run for low-frequency checks.

## Features

- **Serverless & Cost-Effective**: No need to manage servers. Costs are minimal to zero.
- **Criteria-Based Filtering**: Finds tickets based on your desired quantity and maximum price.
- **Stateful Notifications**: Remembers when a notification has been sent to avoid spam.
- **Easy Deployment**: A single script deploys or updates the entire stack.
- **Automated & Reliable**: Runs automatically on a schedule set by you.
- **Professional Testing**: Uses pytest for comprehensive test coverage.
- **Clean Architecture**: Well-organized folder structure for maintainability.

## Prerequisites

Before you begin, ensure you have the following:

1.  An **AWS Account** with access keys configured.
2.  **AWS CLI** installed and configured on your machine.
    ```bash
    aws configure
    ```
3.  **Python 3.9+** installed.
4.  A **Resend API Key** for sending email notifications. You can get one from [resend.com](https://resend.com).

## Quick Start: Deployment

Follow these steps to deploy the Tixel Scraper to your AWS account.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tixel-scraper.git
cd tixel-scraper
```

### 2. Configure Environment Variables

Create a .env file by copying the example. This file will store your secrets and configuration.

```bash
cp .env.example .env
```

Now, edit the .env file with your details:

```dotenv
# .env

# Resend API Key (get from https://resend.com/api-keys)
RESEND_API_KEY=your-resend-api-key-here

# Email addresses
FROM_ADDRESS=notifications@yourdomain.com
TO_ADDRESSES=your-email@example.com,another-email@example.com

# Tixel URL to monitor
TIXEL_URL=https://tixel.com/au/music-tickets/your-event-name

# Your criteria for the tickets
MAX_PRICE=150
DESIRED_QUANTITY=2

# Optional: AWS Stack Name and Region
# STACK_NAME=tixel-scraper
# AWS_REGION=us-east-1
```

### 3. Deploy the Application

Make the deployment script executable and run it from the project root.

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The script will create a dedicated S3 bucket for artifacts, package your Lambda function, and deploy the CloudFormation stack. The scraper will be active immediately after the script finishes.

## Managing the Scraper

You can easily control the scraper without having to redeploy.

### Pause or Resume the Scraper

To temporarily stop the scraper (e.g., after you've bought tickets), you can disable the EventBridge schedule. This is the recommended way to pause the service, and it's free.

```bash
# To PAUSE (replace tixel-scraper with your stack name if you changed it)
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state DISABLED

# To RESUME
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state ENABLED
```

### Update the Configuration

If you want to change the Tixel URL, price, or email addresses:

1. Edit your .env file.

2. Re-run the deployment script:

```bash
./scripts/deploy.sh
```

The script will automatically detect the existing stack and update it with the new configuration.

### View Logs

You can monitor the scraper's activity and check for errors by viewing the CloudWatch logs. The deploy.sh script will output the correct command, but it generally looks like this:

```bash
aws logs tail /aws/lambda/tixel-scraper-tixel-scraper --follow
```

### Permanently Delete the Scraper

If you no longer need the scraper, you can delete all associated AWS resources by deleting the CloudFormation stack.

```bash
aws cloudformation delete-stack --stack-name tixel-scraper
```

## Local Development & Testing

This project uses pytest for robust local testing.

### 1. Install Dependencies

Install the main application dependencies and the development-only dependencies.

```bash
# Install Lambda dependencies
pip install -r src/lambda_requirements.txt

# Install testing dependencies
pip install -r requirements-dev.txt
```

### 2. Run Tests

Ensure your .env file is configured, then run pytest from the project root. pytest will automatically discover and run all tests in the tests directory.

```bash
pytest
```

The tests will mock all external services (like AWS and Resend), so they run quickly and won't incur costs or send real emails.

For more verbose output:

```bash
pytest -v
```

For coverage reporting:

```bash
pytest --cov=src
```

## Project Structure

```
.
├── .github/workflows/deploy.yml    # CI/CD pipeline (optional)
├── infra/
│   └── cloudformation-template.yaml  # Infrastructure definition
├── scripts/
│   └── deploy.sh                   # Deployment script
├── src/
│   ├── email_template.html         # Email notification template
│   ├── lambda_function.py          # Core application logic
│   └── lambda_requirements.txt     # Lambda dependencies
├── tests/
│   ├── __init__.py                 # Makes tests a Python package
│   └── test_lambda_handler.py      # Comprehensive test suite
├── .env.example                    # Configuration template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
└── requirements-dev.txt            # Development dependencies
```

## Testing Strategy

The test suite covers all major scenarios:

- ✅ **First-time ticket discovery**: Sends notification and updates state
- ✅ **No tickets found**: No notification, no state change
- ✅ **Already notified**: No duplicate notifications
- ✅ **State reset**: Resets when tickets disappear
- ✅ **Error handling**: Graceful failure handling

All tests use mocks to avoid external dependencies and costs.

## Security Considerations

- **Secrets Management**: API keys and other secrets are loaded from a local .env file (which is git-ignored) and passed to AWS CloudFormation as secure parameters.

- **IAM Roles**: The resources (Lambda, Scheduler) are configured with narrowly scoped IAM roles to follow the principle of least privilege.

- **Dependencies**: Dependencies are managed in src/lambda_requirements.txt. It's good practice to periodically check for vulnerabilities.

## Disclaimer

This script is for personal, educational purposes only. Web scraping can be against the terms of service of a website. Please ensure you are not violating Tixel's ToS. The creators of this script are not responsible for any misuse.
