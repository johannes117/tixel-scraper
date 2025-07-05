# Testing and CI/CD Setup

This document covers local testing of the Lambda function and setting up automated deployment via GitHub Actions.

## 🧪 Local Testing

### Prerequisites

Install the required dependencies for local testing:

```bash
pip install -r lambda_requirements.txt
pip install python-dotenv
```

### Running Tests Locally

1. **Ensure your `.env` file is configured** with your actual values
2. **Run the local test script**:
   ```bash
   python test_lambda_local.py
   ```

### What the Local Tests Do

The local testing script (`test_lambda_local.py`) provides:

- **Mock AWS Services**: Simulates DynamoDB and other AWS services
- **Mock Email Sending**: Tests email logic without actually sending emails
- **Multiple Test Scenarios**:
  - Real ticket checking (uses your actual Tixel URL)
  - Mock tickets available (forces ticket found scenario)
  - No tickets available (forces no tickets scenario)
- **Environment Simulation**: Replicates Lambda environment variables

### Sample Test Output

```
🚀 Tixel Scraper Lambda - Local Testing
==================================================

1️⃣ Testing normal execution (real ticket check)...
🧪 Testing Lambda function locally...
📧 From: alerts@mydomain.com
📧 To: user@email.com
🔗 URL: https://tixel.com/events/your-event
--------------------------------------------------
✅ Lambda function executed successfully!
📊 Result: {
  "statusCode": 200,
  "body": "{\"message\": \"Ticket check completed successfully\", \"tickets_available\": false, \"notification_sent\": false}"
}
📧 No email notification (no tickets found or already notified)
```

## 🚀 GitHub Actions CI/CD Pipeline

### Setup Instructions

1. **Fork/Clone the repository** to your GitHub account

2. **Set up GitHub Secrets** in your repository settings:

   - Go to `Settings > Secrets and variables > Actions`
   - Add the following secrets:

   | Secret Name             | Description                | Example                                    |
   | ----------------------- | -------------------------- | ------------------------------------------ |
   | `AWS_ACCESS_KEY_ID`     | Your AWS access key        | `AKIAIOSFODNN7EXAMPLE`                     |
   | `AWS_SECRET_ACCESS_KEY` | Your AWS secret key        | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
   | `RESEND_API_KEY`        | Your Resend API key        | `re_abc123xyz`                             |
   | `FROM_ADDRESS`          | Email address to send from | `alerts@mydomain.com`                      |
   | `TO_ADDRESSES`          | Comma-separated recipients | `user1@email.com,user2@email.com`          |
   | `TIXEL_URL`             | Tixel URL to monitor       | `https://tixel.com/events/your-event`      |

3. **Configure the workflow** (optional):
   - Edit `.github/workflows/deploy.yml` if you want to change:
     - AWS region (default: `ap-southeast-2`)
     - Stack name (default: `tixel-scraper`)
     - Trigger conditions

### How the CI/CD Pipeline Works

The pipeline has two main jobs:

#### 1. **Test Job** (runs on every push/PR)

- ✅ Checks out the code
- ✅ Sets up Python environment
- ✅ Installs dependencies
- ✅ Creates test environment
- ✅ Runs local tests to validate the Lambda function

#### 2. **Deploy Job** (runs only on main branch pushes)

- ✅ Runs only after tests pass
- ✅ Configures AWS credentials
- ✅ Creates deployment package
- ✅ Uploads to temporary S3 bucket
- ✅ Deploys/updates CloudFormation stack
- ✅ Updates Lambda function code
- ✅ Cleans up temporary resources

### Triggering Deployments

The pipeline automatically triggers on:

- **Push to main branch**: Full test + deploy
- **Pull requests**: Test only
- **Manual trigger**: You can manually run the workflow from GitHub Actions tab

### Monitoring Deployments

1. **GitHub Actions tab**: View deployment progress and logs
2. **AWS Console**: Monitor the deployed resources
3. **CloudWatch Logs**: View Lambda function execution logs

## 🔧 Advanced Configuration

### Custom Testing Scenarios

You can extend `test_lambda_local.py` to add custom test scenarios:

```python
def test_custom_scenario():
    """Add your custom test logic here"""
    with patch('lambda_function.check_tickets', return_value=True):
        with patch('lambda_function.get_notification_state', return_value={'notification_sent': False}):
            result = test_lambda_function()
    return result
```

### Environment-Specific Deployments

To deploy to different environments (dev, staging, prod):

1. **Create separate workflow files**:

   - `.github/workflows/deploy-dev.yml`
   - `.github/workflows/deploy-prod.yml`

2. **Use different stack names**:

   ```yaml
   env:
     STACK_NAME: tixel-scraper-dev # or tixel-scraper-prod
   ```

3. **Use environment-specific secrets**:
   ```yaml
   environment: production # GitHub environment protection
   ```

### Multi-Region Deployment

To deploy to multiple AWS regions:

```yaml
strategy:
  matrix:
    region: [ap-southeast-2, us-east-1, eu-west-1]
env:
  AWS_REGION: ${{ matrix.region }}
  STACK_NAME: tixel-scraper-${{ matrix.region }}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Tests fail locally**:

   - Check your `.env` file exists and has correct values
   - Ensure all dependencies are installed
   - Verify your Tixel URL is accessible

2. **GitHub Actions deployment fails**:

   - Verify all secrets are set correctly
   - Check AWS credentials have necessary permissions
   - Review CloudFormation events in AWS Console

3. **Lambda function errors after deployment**:
   - Check CloudWatch logs for detailed error messages
   - Verify environment variables are set correctly
   - Test the function manually in AWS Console

### Required AWS Permissions

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "dynamodb:*",
        "iam:*",
        "s3:*",
        "scheduler:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 📊 Monitoring and Alerts

### GitHub Actions Notifications

Set up notifications for deployment status:

1. **Repository Settings > Notifications**
2. **Enable Actions notifications**
3. **Configure email/Slack integration**

### AWS CloudWatch Alarms

Add monitoring alarms to your CloudFormation template:

```yaml
LambdaErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub "${AWS::StackName}-lambda-errors"
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```

## 🎯 Best Practices

1. **Always test locally** before pushing to main branch
2. **Use pull requests** for code reviews
3. **Monitor deployment logs** for issues
4. **Keep secrets secure** and rotate them regularly
5. **Use environment protection** for production deployments
6. **Set up monitoring** and alerts for your Lambda function

---

This setup provides a robust development and deployment pipeline for your Tixel scraper! 🚀
