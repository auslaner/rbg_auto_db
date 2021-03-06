#!/bin/bash

# Get our IDs by sourcing the config file
source aws_vpn.conf

aws ec2 disassociate-client-vpn-target-network \
	--client-vpn-endpoint-id $ENDPOINTID \
	--association-id $ASSOCIATIONID
