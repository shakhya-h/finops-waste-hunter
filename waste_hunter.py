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

# import boto3
# import os
# import requests
# import json

# def send_slack_alert(message):
#     webhook_url = os.getenv('SLACK_WEBHOOK_URL')
#     if webhook_url:
#         payload = {"text": message}
#         requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

# def hunt_elastic_ips(ec2_client, region):
#     print(f"--- Scanning Elastic IPs in {region} ---")
#     addresses = ec2_client.describe_addresses()
#     found_ip_waste = False
    
#     for addr in addresses['Addresses']:
#         # If 'InstanceId' is missing, the IP is NOT attached to anything
#         if 'InstanceId' not in addr:
#             ip_msg = f"📍 *FinOps Alert*: Unused Elastic IP `{addr['PublicIp']}` found in `{region}`. Delete it to save costs!"
#             print(ip_msg)
#             send_slack_alert(ip_msg)
#             found_ip_waste = True
#     return found_ip_waste

# def hunt_volumes(ec2_resource, region):
#     print(f"--- Scanning EBS Volumes in {region} ---")
#     found_vol_waste = False
#     for volume in ec2_resource.volumes.all():
#         if volume.state == 'available':
#             vol_msg = f"💸 *FinOps Alert*: Unattached EBS Volume `{volume.id}` found in `{region}`. Size: {volume.size}GB."
#             print(vol_msg)
#             send_slack_alert(vol_msg)
#             found_vol_waste = True
#     return found_vol_waste

# def main():
#     region = 'eu-north-1'
#     # We need both 'resource' and 'client' for different AWS tasks
#     ec2_resource = boto3.resource('ec2', region_name=region)
#     ec2_client = boto3.client('ec2', region_name=region)
    
#     v_waste = hunt_volumes(ec2_resource, region)
#     ip_waste = hunt_elastic_ips(ec2_client, region)
    
#     if not v_waste and not ip_waste:
#         print("Everything is clean! No waste detected.")

# if __name__ == "__main__":
#     main()

import boto3
import os
import requests
import json

# --- PRICING CONSTANTS (Monthly Estimates) ---
EBS_PRICE_PER_GB = 0.10   # Standard gp3 pricing
IDLE_IP_PRICE    = 3.60   # $0.005/hr * 730 hours

def send_slack_alert(message):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if webhook_url:
        payload = {"text": message}
        requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

def hunt_elastic_ips(ec2_client, region):
    print(f"--- Scanning Elastic IPs in {region} ---")
    addresses = ec2_client.describe_addresses()
    savings = 0.0
    
    for addr in addresses['Addresses']:
        if 'InstanceId' not in addr:
            ip_msg = f"📍 *Unused IP Found*: `{addr['PublicIp']}`. Waste: ${IDLE_IP_PRICE}/mo"
            print(ip_msg)
            # send_slack_alert(ip_msg) # Optional: Uncomment if you want individual alerts
            savings += IDLE_IP_PRICE
            
    return savings

def hunt_volumes(ec2_resource, region):
    print(f"--- Scanning EBS Volumes in {region} ---")
    savings = 0.0
    
    for volume in ec2_resource.volumes.all():
        if volume.state == 'available':
            vol_cost = volume.size * EBS_PRICE_PER_GB
            vol_msg = f"💿 *Unused Volume Found*: `{volume.id}` ({volume.size}GB). Waste: ${vol_cost:.2f}/mo"
            print(vol_msg)
            # send_slack_alert(vol_msg) # Optional: Uncomment if you want individual alerts
            savings += vol_cost
            
    return savings

def main():
    region = 'eu-north-1'
    ec2_resource = boto3.resource('ec2', region_name=region)
    ec2_client = boto3.client('ec2', region_name=region)
    
    # Get savings from each function
    vol_savings = hunt_volumes(ec2_resource, region)
    ip_savings = hunt_elastic_ips(ec2_client, region)
    
    total_savings = vol_savings + ip_savings
    
    # Send one consolidated summary message
    if total_savings > 0:
        summary_msg = (
            f"💰 *FinOps Weekly Report* ({region})\n"
            f"-------------------------------------\n"
            f"• Unused Volumes Cost: ${vol_savings:.2f}/mo\n"
            f"• Idle IPs Cost:       ${ip_savings:.2f}/mo\n"
            f"-------------------------------------\n"
            f"🚨 *Total Potential Savings: ${total_savings:.2f} / month*"
        )
        print(summary_msg)
        send_slack_alert(summary_msg)
    else:
        print("✅ System Clean: No waste detected.")

if __name__ == "__main__":
    main()
