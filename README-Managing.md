# Managing and Stopping the Tixel Scraper

This document explains how to manage the running state of your Tixel Scraper on AWS. Because the scraper runs on a schedule, it's important to know how to pause or stop it completely to prevent incurring unwanted costs, especially after you've found the tickets you were looking for.

There are two primary methods to control the scraper:

1.  **Pause the Scraper**: Temporarily disable the trigger. (Recommended)
2.  **Delete the Scraper**: Permanently remove all associated AWS resources.

---

## ⏸️ Method 1: Pause the Scraper (Recommended)

This is the best option if you've found your tickets but might want to use the scraper again for a different event. You simply disable the schedule that triggers the Lambda function.

- **Cost Impact**: Costs will drop to nearly zero (pennies per month for storing the DynamoDB item).
- **What it Does**: Stops the Lambda function from being invoked. All resources remain in your account, ready to be re-activated.
- **Reversibility**: Instantly reversible.

### Using the AWS Console (Easiest)

1.  Log in to the **AWS Console**.
2.  Navigate to the **Amazon EventBridge** service.
3.  In the left-hand menu, click on **Schedules**.
4.  Find your schedule in the list. By default, it will be named `tixel-scraper-tixel-scraper-schedule`.
5.  Select the checkbox next to the schedule and click the **Disable** button.

To resume the scraper later, follow the same steps and click **Enable**.

### Using the AWS CLI (Command Line)

You can also control the schedule from your terminal.

**To PAUSE the scraper:**

```bash
# Replace the schedule name if you used a custom STACK_NAME
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state DISABLED

# Expected output:
# {
#     "ScheduleArn": "arn:aws:scheduler:REGION:ACCOUNT_ID:schedule/default/tixel-scraper-tixel-scraper-schedule"
# }
```

**To RESUME the scraper later:**

```bash
aws scheduler update-schedule --name tixel-scraper-tixel-scraper-schedule --state ENABLED
```

---

## 🗑️ Method 2: Permanently Delete the Scraper

Use this method if you are completely finished with the scraper and want to remove all its resources to ensure there are no future costs.

- **Cost Impact**: Costs will drop to **absolute zero**.
- **What it Does**: Deletes the CloudFormation stack, which removes the Lambda function, DynamoDB table, IAM roles, and the EventBridge schedule.
- **Reversibility**: Not reversible. To get the scraper back, you must run the `./deploy.sh` script again.

### Using the AWS Console

1.  Log in to the **AWS Console**.
2.  Navigate to the **AWS CloudFormation** service.
3.  Select the **Stacks** view.
4.  Find and select your stack. By default, it is named `tixel-scraper`.
5.  Click the **Delete** button and confirm the deletion.

The stack status will change to `DELETE_IN_PROGRESS`. This process may take a few minutes.

### Using the AWS CLI (Command Line)

This command will start the deletion process for all resources in the stack.

```bash
# Replace the stack name if you used a custom one
aws cloudformation delete-stack --stack-name tixel-scraper
```

---

## Summary: Pause vs. Delete

| Feature            | Method 1: Pause (Disable Schedule)                                | Method 2: Delete (Delete Stack)                                      |
| ------------------ | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Best For**       | Temporarily stopping, or if you might use it again.               | You're completely done and want to clean up everything.              |
| **Cost**           | Drops to near-zero (a few cents per month).                       | Drops to **absolute zero**.                                          |
| **Reversibility**  | Instantly reversible. Just click "Enable".                        | Permanent. You must redeploy to get it back.                         |
| **What Happens**   | The trigger is turned off. The resources remain but are inactive. | All resources (Lambda, DB, Roles, Schedule) are permanently removed. |
| **Recommendation** | **Start with this one.** It's the safest and easiest option.      | Use this for a final, complete cleanup.                              |
