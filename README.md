# CloudWatch-Log-Normalizer
The CloudWatch Log Normalizer project involves setting up an automated system to read logs from AWS CloudWatch, normalize the log data, and store the normalized logs in an AWS S3 bucket. This system will help in managing and analyzing log data more efficiently.

## Create Config File
1. Create file with name 'config.ini'

    [Dev]
   
       aws_access_key_id = <aws_access_key_id>
   
       aws_secret_key = <aws_secret_key>
