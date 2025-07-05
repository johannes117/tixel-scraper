# Tixel Scraper - AWS Lambda Version

A serverless Tixel ticket availability scraper that runs on AWS Lambda, providing cost-effective monitoring without the need for a dedicated server.

## 🏗️ Architecture

This serverless solution uses:

- **AWS Lambda**: Runs the scraping logic
- **DynamoDB**: Stores notification state
- **EventBridge Scheduler**: Triggers the function every 60 seconds
- **CloudWatch Logs**: Monitors execution and errors
- **Resend API**: Sends email notifications

## 💰 Cost Benefits

- **$0/month** on AWS Free Tier (first 12 months)
- **~$1-2/month** after free tier (based on 43,200 invocations/month)
- No server maintenance or VPS costs
- Automatic scaling and high availability

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Resend API Key** for email notifications
4. **Python 3.9+** for local development (optional)

## 🚀 Quick Deployment

1. **Clone and navigate to the repository**

   ```bash
   git clone <your-repo>
   cd tixel-scraper
   ```

2. **Create your configuration file**

   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Configure your .env file**

   ```bash
   # Example .env content:
   RESEND_API_KEY=re_abc123xyz
   FROM_ADDRESS=alerts@mydomain.com
   TO_ADDRESSES=user1@email.com,user2@email.com
   TIXEL_URL=https://tixel.com/events/example-event
   ```

4. **Make the deployment script executable**

   ```bash
   chmod +x deploy.sh
   ```

5. **Deploy the Lambda function**

   ```bash
   ./deploy.sh
   ```

6. **Monitor deployment**
   The script will output useful commands for monitoring your deployment.

## 📁 File Structure

```
tixel-scraper/
├── lambda_function.py              # Main Lambda handler
├── lambda_requirements.txt         # Python dependencies for Lambda
├── cloudformation-template.yaml    # AWS infrastructure template
├── deploy.sh                      # Deployment script
├── env.example                    # Environment variables template
├── .env                          # Your actual configuration (create from env.example)
├── test_lambda_local.py           # Local testing script
├── .github/workflows/deploy.yml   # GitHub Actions CI/CD pipeline
├── README-Lambda.md               # This file
├── README-Testing-CICD.md         # Testing and CI/CD documentation
└── (original files...)
```

## 🔧 Configuration

### Environment Variables (Set automatically by CloudFormation)

- `RESEND_API_KEY`: Your Resend API key
- `FROM_ADDRESS`: Email address to send from
- `TO_ADDRESSES`: Comma-separated list of recipient emails
- `TIXEL_URL`: The Tixel URL to monitor
- `DYNAMODB_TABLE_NAME`: DynamoDB table name (auto-generated)

### Scheduling

The function runs every 60 seconds by default. To change this:

1. Update the `ScheduleExpression` in `cloudformation-template.yaml`
2. Redeploy using the deployment script

Common schedule expressions:

- `rate(1 minute)` - Every minute
- `rate(5 minutes)` - Every 5 minutes
- `rate(1 hour)` - Every hour

## 📊 Monitoring and Management

### View Logs

```bash
aws logs tail /aws/lambda/tixel-scraper-tixel-scraper --follow
```

### Test Function Manually

```bash
aws lambda invoke --function-name tixel-scraper-tixel-scraper --payload '{}' response.json
cat response.json
```

### Check Notification State

```bash
aws dynamodb scan --table-name tixel-scraper-notification-state
```

### Pause/Resume Scraping

```bash
# Pause
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state DISABLED

# Resume
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state ENABLED
```

## 🛠️ Troubleshooting

### Common Issues

1. **Deployment fails with permissions error**

   - Ensure your AWS user has IAM, Lambda, DynamoDB, and EventBridge permissions
   - Try running `aws sts get-caller-identity` to verify credentials

2. **Function times out**

   - Check CloudWatch logs for specific errors
   - Verify the Tixel URL is accessible

3. **No emails received**

   - Verify Resend API key is correct
   - Check sender email is verified in Resend
   - Look for email delivery errors in CloudWatch logs

4. **Function not triggering**
   - Check EventBridge Scheduler status
   - Verify Lambda permissions are set correctly

### Debug Commands

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name tixel-scraper

# View recent logs
aws logs filter-log-events --log-group-name /aws/lambda/tixel-scraper-tixel-scraper --start-time $(date -d '1 hour ago' +%s)000

# Check DynamoDB table
aws dynamodb describe-table --table-name tixel-scraper-notification-state
```

## 🔄 Updates and Maintenance

### Update Lambda Code

After modifying `lambda_function.py`, redeploy:

```bash
./deploy.sh
```

### Update Configuration

To change email addresses, Tixel URL, or other settings:

1. **Edit your .env file** with new values
2. **Run the update command**:
   ```bash
   ./deploy.sh update
   ```

**Note**: The `update` parameter is optional - the script will automatically detect if the stack exists and update it accordingly.

### Delete Everything

```bash
aws cloudformation delete-stack --stack-name tixel-scraper
```

## 📈 Scaling and Customization

### Multiple Events

To monitor multiple Tixel URLs, deploy separate stacks:

```bash
./deploy.sh "api-key" "from@email.com" "to@email.com" "url1"
# Change STACK_NAME in deploy.sh and run again for url2
```

### Custom Notification Logic

Modify the `check_tickets()` function in `lambda_function.py` to:

- Look for specific ticket types
- Check price ranges
- Add custom filtering logic

### Different Notification Channels

Extend the `send_email()` function to support:

- SMS via AWS SNS
- Slack webhooks
- Discord notifications

## 🔒 Security Best Practices

- API keys are stored as CloudFormation parameters (encrypted)
- Lambda function has minimal IAM permissions
- DynamoDB table uses pay-per-request billing
- CloudWatch logs have 14-day retention

## 📞 Support

For issues specific to:

- **AWS deployment**: Check CloudFormation events and CloudWatch logs
- **Email delivery**: Verify Resend API key and sender verification
- **Tixel scraping**: Ensure the URL format hasn't changed

## 🧪 Testing and CI/CD

For local testing and automated deployment setup, see:

- **[Local Testing Guide](README-Testing-CICD.md#-local-testing)** - Test your Lambda function locally before deployment
- **[CI/CD Pipeline Setup](README-Testing-CICD.md#-github-actions-cicd-pipeline)** - Automated deployment via GitHub Actions

### Quick Local Test

```bash
# Install dependencies
pip install -r lambda_requirements.txt python-dotenv

# Run local tests
python test_lambda_local.py
```

## 🎯 Next Steps

1. **Test locally** using `python test_lambda_local.py`
2. **Deploy using the script** or set up GitHub Actions for automated deployment
3. **Monitor the first few runs** to ensure everything works correctly
4. **Set up CloudWatch alarms** for Lambda errors (optional)
5. **Consider adding a dashboard** using CloudWatch or third-party tools
6. **Customize the email template** for your specific needs

---

**Happy ticket hunting! 🎫**
