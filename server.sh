#!/bin/bash

# Default values for instance ID and region
INSTANCE_ID=""
REGION="us-west-2"  # Default region, can be overridden by the user

# Function to display usage information
usage() {
    echo "Usage: $0 --instance-id <instance-id> --region <region> --action <start|stop>"
    echo "  --instance-id: EC2 Instance ID (e.g., i-xxxxxxxxxxxxxxxxx)"
    echo "  --region: AWS Region (e.g., us-west-2)"
    echo "  --action: Action to perform (start or stop)"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --instance-id)
            INSTANCE_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --action)
            ACTION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Check if the required parameters are provided
if [[ -z "$INSTANCE_ID" ]] || [[ -z "$ACTION" ]]; then
    usage
fi

# Function to start the EC2 instance
start_instance() {
    echo "Starting EC2 instance $INSTANCE_ID in region $REGION..."
    aws ec2 start-instances --instance-ids "$INSTANCE_ID" --region "$REGION"
    if [ $? -eq 0 ]; then
        echo "EC2 instance $INSTANCE_ID started successfully."
        # Get the public IP address after starting
        INSTANCE_PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query "Reservations[0].Instances[0].PublicIpAddress" --output text --region "$REGION")
        echo "Public IP Address: $INSTANCE_PUBLIC_IP"
    else
        echo "Failed to start EC2 instance $INSTANCE_ID."
    fi
}

# Function to stop the EC2 instance
stop_instance() {
    echo "Stopping EC2 instance $INSTANCE_ID in region $REGION..."
    aws ec2 stop-instances --instance-ids "$INSTANCE_ID" --region "$REGION"
    if [ $? -eq 0 ]; then
        echo "EC2 instance $INSTANCE_ID stopped successfully."
    else
        echo "Failed to stop EC2 instance $INSTANCE_ID."
    fi
}

# Perform the appropriate action based on the user input
if [ "$ACTION" == "start" ]; then
    start_instance
elif [ "$ACTION" == "stop" ]; then
    stop_instance
else
    echo "Invalid action: $ACTION"
    usage
fi
