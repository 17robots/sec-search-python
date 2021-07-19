import boto3


def grab_sec_groups():
    ec2 = boto3.client('ec2', region_name="us-west-2")
    ec2_regions = [region['RegionName']
                   for region in ec2.describe_regions()['Regions']]

    for region in ec2_regions:
        conn = boto3.client('ec2', region_name=region)
        print(region)
        sec_groups = conn.describe_security_groups(MaxResults=100)
        print(sec_groups['SecurityGroups'])
