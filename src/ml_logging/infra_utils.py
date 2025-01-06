import os
from boto3 import client 


def _get_public_ip(instance_id):
    ec2_client = client(
        "ec2", 
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"], 
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_DEFAULT_REGION"]
    )
    
    response = ec2_client.describe_instances(InstanceIds=[instance_id])

    reservation = response["Reservations"][0]
    instance = reservation["Instances"][0]
    public_ip = instance.get("PublicIpAddress", None)

    return public_ip
