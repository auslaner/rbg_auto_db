# Prerequisites
- [AWS CLI v. 2](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- AWS CLI credentials
- Docker
- [JQ](https://stedolan.github.io/jq/) 
- Python3

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

Install prerequisites. JQ can be installed on Mac with homebrew:

`brew install jq`

Install required packages:

`pip install -r requirements.txt`

# Usage

Run `main.py`. The script will take from ~11-70 minutes to complete depending on how quickly the AWS VPN Gateway becomes
available. Occasionally, it seems to get stuck in the 'pending' state and will not accept connections. When this is the 
case, simply re-run the script to try again.

Tested with python version 3.9.1.

# Troubleshooting

If the postgres docker container fails to connect to the RDS instance to dump the database, visit AWS's VPC admin portal
and view the Client VPN Endpoint section to see if the endpoint is in an 'available' state. If not, it may just need
more time to become ready.

If the VPN endpoint is available but the docker container is still failing to connect, it may be that an old version of
the vpn-client container is still running. This can happen if the script starts the container but then is interrupted
before it can clean up the containers. To resolve this, simply stop and remove the vpn-client container and restart the
script.

`docker stop vpn-client && docker rm vpn-client`

# Further Considerations

Please note that if the script is interrupted before completion, an AWS Client VPN Endpoint created by the script may 
still exist. AWS charges for these endpoints so you will probably want to delete them manually before re-running.