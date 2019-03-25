# AWSAlexaWPNewPostCount
This is a basic Lambda function to hook in to your Wordpress database (or any RDS based database for that matter) and retrieve the number of new posts made today and the total number of posts made this month.

What to do:

1) Create an empty Python 3.7 Lambda function.

2) Upload this function.

3) Update the database information in the lambda_function.py file:

rds_host  = "YOUR DATABASE CONNECTION STRING"
rds_username = "YOUR DATABASE USERNAME"
rds_password = "YOUR DATABASE PASSWORD"
rds_db_name = "YOUR DATABASE NAME"

4) Create the skill in the Alexa Developer Console: https://developer.amazon.com/alexa/console/ask
