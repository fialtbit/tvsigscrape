# Crypto signal data collection using the TradeView

## Deployment instructions
These instructions assume you are using a Unix based system (Linux or macOS) running a bash terminal.

1. Install [Apex](http://apex.run), a tool for managing and deploying serverless funtions on AWS Lambda, by running

 ```
 curl https://raw.githubusercontent.com/apex/apex/master/install.sh | sh
 ```
 from your terminal.
2. Ensure your AWS keys are managed correctly, as per the Apex docs - see the [AWS docs](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) for more details.
3. Install Python 3.6.x - [here](https://medium.com/@smoothml/my-python-development-setup-bbbe3715a474) is a blog I wrote on how I configure my Python development environment.
4. Create a folder for the project, e.g. `crypto_data`, and navigate into it with `cd crypto_data`.
5. Initialise an Apex project with `apex init`. This will create the required AWS roles for the function to run. Note, the profile you're using must have appropriate permissions, as described in the Apex docs.
6. We need to add permission for the function to write to S3, so on the AWS console navigate to your IAM dashboard, choose roles on the left hand side and select the role created by Apex - assuming you also named the project `crypto_data` during the Apex initialisation, the role will be named `crypto_data_lambda_function`.
 ![](screenshots/lambda_role.png)
 Add the following as an inline policy by clicking "Add inline policy" in the bottom right, followed by "{}JSON" and "Edit policy", replacing `<your-bucket-name> appropriately.
 
 ```
 {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "s3:PutObject"
              ],
              "Resource": [
                  "arn:aws:s3:::<your-bucket-name>/*"
              ]
        }
      ]
 }
 ```
 ![](screenshots/s3_policy.png)

7. Back in your terminal now, remove the hello world function created by Apex: `rm -r functions/hello`.
8. In the `project.json` file, increase the timeout from 5 to 30 - how many seconds until the Lambda function stops after initialisation.
9. Copy the functions from the zip file I gave you into the functions folder in your project. Your project tree should look something like this:

 ```
├── functions
│   ├── BIN_NEO_15
│   │   ├── clean-up.sh
│   │   ├── function.json
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── BIN_NEO_1D
│   │   ├── clean-up.sh
│   │   ├── function.json
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── BIT_ADA_60
│   │   ├── clean-up.sh
│   │   ├── function.json
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── BIT_KEY_240
│   │   ├── clean-up.sh
│   │   ├── function.json
│   │   ├── main.py
│   │   └── requirements.txt
│   └── KRA_BTC_120
│       ├── clean-up.sh
│       ├── function.json
│       ├── main.py
│       └── requirements.txt
├── project.json
 ```
 
10. In each of the `main.py` files, update the `BUCKET_NAME` variable (defined near the top of each file) from `<your-bucket-name>` to the name of the bucket to which you're writing the data.
11. Deploy the functions with `apex deploy`. You can test their executions by running `apex invoke` e.g. `apex invoke collect-tickers`.
12. You need to set up your desired execution schedule (e.g. every five minutes) from the AWS console. Go to the Lambda dashboard, where you should see a list of the five functions. Click on one to go to its cofiguration page. Add a CloudWatch event trigger, then create a new rule.
 ![](screenshots/cloudwatch_event.png)
 You can use cron expressions to create the rule, which you can generate using [this](http://www.cronmaker.com) site. The expression for an execution evey five minutes is `0 0/5 * 1/1 * ? *`, so add this in the schedule expression box.
 ![](screenshots/cron_rule.png)
13. Make a cup of tea and wait for the data to roll in!
  
