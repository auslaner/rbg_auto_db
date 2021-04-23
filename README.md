# Prerequisites
- Docker
- Python3
- AWS CLI credentials

# Setup

First, create the `creds.env` file in the same directory as this file. In it, define the following using
`VARIABLE=VALUE` syntax:

1. `PGPASSWORD` as the password to the database being dumped
2. `PGHOST` as the internal IP address of the RDS instance within the AWS VPC
3. `PGUSERNAME` as the username used to connect to the database
4. `PGDB` as the name of the database
5. `SERVER_CERT_ARN` as the AWS ARN of the certificate to be used as the AWS VPN Gateway server certificate
6. `CLIENT_ROOT_CERT_ARN` as the AWS ARN of the root client certificate

Then, create the directories `backups` and `certs`. Place your client certificate and key files in the `certs` 
directory.

# Usage

Run `main.py`. The script will take from ~11-70 minutes to complete depending on how quickly the AWS VPN Gateway becomes
available. Occasionally, it seems to get stuck in the 'pending' state and will not accept connections. When this is the 
case, simply re-run the script to try again.

Tested with python version 3.9.1.