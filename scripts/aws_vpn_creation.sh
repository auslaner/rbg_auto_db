#!/bin/bash

source creds.env

# Clear config file so we can use it later to delete what we create here
echo '' > aws_vpn.conf

# Clear the existing ovpn config file
echo '' > aws_gateway.ovpn

# shellcheck disable=SC1083
output=$(aws ec2 create-client-vpn-endpoint \
	--client-cidr-block "10.0.16.0/22" \
	--server-certificate-arn $SERVER_CERT_ARN \
	--authentication-options Type=certificate-authentication,MutualAuthentication={ClientRootCertificateChainArn="$CLIENT_ROOT_CERT_ARN"} \
	--connection-log-options Enabled=False)

# Get the client endpoint ID from the output
endpointID=$(echo "$output" | jq -r '.ClientVpnEndpointId')
echo "$output"
echo "Created VPN Client Endpoint with ID: $endpointID"
sleep 5

# Associate a subnet with the client endpoint
output=$(aws ec2 associate-client-vpn-target-network \
	--subnet-id subnet-0ead106100ce8a53a \
	--client-vpn-endpoint-id "$endpointID")

# Get the association ID from the output
associationID=$(echo "$output" | jq -r '.AssociationId')
echo "$output"
echo "Created association between VPN endpoint and RDS subnet with ID: $associationID"
sleep 5

# Authorize client access to RDS network
aws ec2 authorize-client-vpn-ingress \
	--client-vpn-endpoint-id "$endpointID" \
	--target-network-cidr 10.0.12.0/22 \
	--authorize-all-groups

sleep 5

# Download the client VPN endpoint configuration file
aws ec2 export-client-vpn-client-configuration \
	--client-vpn-endpoint-id "$endpointID" \
	--output text > aws_gateway.ovpn

# Save variables to config file so deletion script can use them
echo "ENDPOINTID=$endpointID" >> aws_vpn.conf
echo "ASSOCIATIONID=$associationID" >> aws_vpn.conf
