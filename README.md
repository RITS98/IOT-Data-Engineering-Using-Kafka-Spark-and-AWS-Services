# IOT-Data-Engineering-Using-Kafka-Spark-and-AWS-Services






## Setup Steps


### Create a connection in Apache Airflow
1. Go to Admin -> Connections -> Add Connection
2. Give a name
3. Add the credentials.
If the AWS credentials is already set in the local computer, we can get it using -
`aws configure export-credentials`
<img width="1695" height="864" alt="image" src="https://github.com/user-attachments/assets/cdf59926-3ac6-46e1-9b95-c0300bbeda48" />

To set up AWS credentials in local computer, follow the below steps
1. Go to IAM service in AWS
2. Click on `My Quick Credentials`
<img width="1676" height="813" alt="image" src="https://github.com/user-attachments/assets/4b8d9e36-1c07-4576-9ace-285836d2999b" />
3. Create a Access Key as given below
<img width="1676" height="787" alt="image" src="https://github.com/user-attachments/assets/c166990e-22de-4ee8-b5f8-2cc66cf126c8" />
4. Set up the credentials in local environment
```
export AWS_ACCESS_KEY_ID=[YOUR ACCESS KEY]
export AWS_SECRET_ACCESS_KEY=[YOUR SECRET KEY]
export AWS_DEFAULT_REGION=[YOUR REGION]
```

5. Check if it is working
```
aws s3 ls  # list s3 buckets, should not throw an error
```


### Create AWS S3 Bucket
1. Go to S3 service in AWS.
2. Click on `Create Bucket`.
3. Fill the Create Bucket application as given below and click on `Create Bucket`
<img width="3342" height="4361" alt="image" src="https://github.com/user-attachments/assets/5a379fa6-13ec-4484-97db-9f21b7d23e31" />

<img width="1110" height="311" alt="image" src="https://github.com/user-attachments/assets/73391ac8-1c6d-4fd8-b8b7-a139763b8e9c" />
