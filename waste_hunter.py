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

import boto3
import os
import requests
import json

def send_slack_alert(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        payload = {"text": message}
        requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

def hunt_waste():
    region = 'eu-north-1'
    ec2 = boto3.resource('ec2', region_name=region)
    print(f"--- Scanning Region: {region} ---")
    
    found_waste = False
    
    for volume in ec2.volumes.all():
        if volume.state == 'available':
            alert_msg = f"💸 *FinOps Alert*: Unattached EBS Volume `{volume.id}` found in `{region}`. Size: {volume.size}GB. Potential waste detected!"
            print(alert_msg)
            send_slack_alert(alert_msg)
            found_waste = True
            
    if not found_waste:
        print("Success! No zombie volumes found.")

if __name__ == "__main__":
    hunt_waste()
