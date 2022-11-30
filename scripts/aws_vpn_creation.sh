#!/bin/bash

source creds.env

# Clear config file so we can use it later to delete what we create here
echo '' > aws_vpn.conf

# Clear the existing ovpn config file
echo '' > aws_gateway.ovpn

# Associate a subnet with the client endpoint
output=$(aws ec2 associate-client-vpn-target-network \
	--subnet-id subnet-06639d8eca95c994f \
	--client-vpn-endpoint-id "$ENDPOINTID")

# Get the association ID from the output
associationID=$(echo "$output" | jq -r '.AssociationId')
echo "$output"
echo "Created association between VPN endpoint and RDS subnet with ID: $associationID"
sleep 5

# Download the client VPN endpoint configuration file
aws ec2 export-client-vpn-client-configuration \
	--client-vpn-endpoint-id "$ENDPOINTID" \
	--output text > aws_gateway.ovpn

# Save variables to config file so deletion script can use them
echo "ENDPOINTID=$ENDPOINTID" >> aws_vpn.conf  # This way aws_vpn_deletion only needs to source one file
echo "ASSOCIATIONID=$associationID" >> aws_vpn.conf
