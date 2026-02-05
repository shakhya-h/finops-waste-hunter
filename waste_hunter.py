# import boto3
# import os

# def hunt_waste():
#     # 1. Set the Region
#     region = 'eu-north-1'
    
#     # 2. Initialize the EC2 Resource
#     # This automatically looks for environment variables
#     try:
#         ec2 = boto3.resource('ec2', region_name=region)
        
#         print(f"--- Scanning Region: {region} ---")
        
#         found_waste = False
        
#         # This is where the script actually tries to talk to AWS
#         for volume in ec2.volumes.all():
#             if volume.state == 'available':
#                 print(f"ALERT: Unattached Volume Found!")
#                 print(f"ID: {volume.id} | Size: {volume.size}GB")
#                 found_waste = True
                
#         if not found_waste:
#             print("Success! No zombie volumes found.")
            
#     except Exception as e:
#         print(f"FAILED: {e}")

# if __name__ == "__main__":
#     hunt_waste()

# import boto3
# import os
# import requests
# import json

# def send_slack_alert(message):
#     webhook_url = os.getenv('SLACK_WEBHOOK_URL')
#     if webhook_url:
#         payload = {"text": message}
#         requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

# def hunt_waste():
#     region = 'eu-north-1'
#     ec2 = boto3.resource('ec2', region_name=region)
#     print(f"--- Scanning Region: {region} ---")
    
#     found_waste = False
    
#     for volume in ec2.volumes.all():
#         if volume.state == 'available':
#             alert_msg = f"💸 *FinOps Alert*: Unattached EBS Volume `{volume.id}` found in `{region}`. Size: {volume.size}GB. Potential waste detected!"
#             print(alert_msg)
#             send_slack_alert(alert_msg)
#             found_waste = True
            
#     if not found_waste:
#         print("Success! No zombie volumes found.")

# if __name__ == "__main__":
#     hunt_waste()

import boto3
import os
import requests
import json

def send_slack_alert(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        payload = {"text": message}
        requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

def hunt_elastic_ips(ec2_client, region):
    print(f"--- Scanning Elastic IPs in {region} ---")
    addresses = ec2_client.describe_addresses()
    found_ip_waste = False
    
    for addr in addresses['Addresses']:
        # If 'InstanceId' is missing, the IP is NOT attached to anything
        if 'InstanceId' not in addr:
            ip_msg = f"📍 *FinOps Alert*: Unused Elastic IP `{addr['PublicIp']}` found in `{region}`. Delete it to save costs!"
            print(ip_msg)
            send_slack_alert(ip_msg)
            found_ip_waste = True
    return found_ip_waste

def hunt_volumes(ec2_resource, region):
    print(f"--- Scanning EBS Volumes in {region} ---")
    found_vol_waste = False
    for volume in ec2_resource.volumes.all():
        if volume.state == 'available':
            vol_msg = f"💸 *FinOps Alert*: Unattached EBS Volume `{volume.id}` found in `{region}`. Size: {volume.size}GB."
            print(vol_msg)
            send_slack_alert(vol_msg)
            found_vol_waste = True
    return found_vol_waste

def main():
    region = 'eu-north-1'
    # We need both 'resource' and 'client' for different AWS tasks
    ec2_resource = boto3.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    
    v_waste = hunt_volumes(ec2_resource, region)
    ip_waste = hunt_elastic_ips(ec2_client, region)
    
    if not v_waste and not ip_waste:
        print("Everything is clean! No waste detected.")

if __name__ == "__main__":
    main()
