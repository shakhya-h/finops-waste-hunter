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

# import boto3
# import os
# import requests
# import json

# # --- PRICING CONSTANTS (Monthly Estimates) ---
# EBS_PRICE_PER_GB = 0.10   # Standard gp3 pricing
# IDLE_IP_PRICE    = 3.60   # $0.005/hr * 730 hours

# def send_slack_alert(message):
#     webhook_url = os.getenv('SLACK_WEBHOOK_URL')
#     if webhook_url:
#         payload = {"text": message}
#         requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

# def hunt_elastic_ips(ec2_client, region):
#     print(f"--- Scanning Elastic IPs in {region} ---")
#     addresses = ec2_client.describe_addresses()
#     savings = 0.0
    
#     for addr in addresses['Addresses']:
#         if 'InstanceId' not in addr:
#             ip_msg = f"📍 *Unused IP Found*: `{addr['PublicIp']}`. Waste: ${IDLE_IP_PRICE}/mo"
#             print(ip_msg)
#             # send_slack_alert(ip_msg) # Optional: Uncomment if you want individual alerts
#             savings += IDLE_IP_PRICE
            
#     return savings

# def hunt_volumes(ec2_resource, region):
#     print(f"--- Scanning EBS Volumes in {region} ---")
#     savings = 0.0
    
#     for volume in ec2_resource.volumes.all():
#         if volume.state == 'available':
#             vol_cost = volume.size * EBS_PRICE_PER_GB
#             vol_msg = f"💿 *Unused Volume Found*: `{volume.id}` ({volume.size}GB). Waste: ${vol_cost:.2f}/mo"
#             print(vol_msg)
#             # send_slack_alert(vol_msg) # Optional: Uncomment if you want individual alerts
#             savings += vol_cost
            
#     return savings

# def main():
#     region = 'eu-north-1'
#     ec2_resource = boto3.resource('ec2', region_name=region)
#     ec2_client = boto3.client('ec2', region_name=region)
    
#     # Get savings from each function
#     vol_savings = hunt_volumes(ec2_resource, region)
#     ip_savings = hunt_elastic_ips(ec2_client, region)
    
#     total_savings = vol_savings + ip_savings
    
#     # Send one consolidated summary message
#     if total_savings > 0:
#         summary_msg = (
#             f"💰 *FinOps Weekly Report* ({region})\n"
#             f"-------------------------------------\n"
#             f"• Unused Volumes Cost: ${vol_savings:.2f}/mo\n"
#             f"• Idle IPs Cost:       ${ip_savings:.2f}/mo\n"
#             f"-------------------------------------\n"
#             f"🚨 *Total Potential Savings: ${total_savings:.2f} / month*"
#         )
#         print(summary_msg)
#         send_slack_alert(summary_msg)
#     else:
#         print("✅ System Clean: No waste detected.")

# if __name__ == "__main__":
#     main()

# import boto3
# import os
# import requests
# import json
# from datetime import datetime, timezone, timedelta

# # --- PRICING CONSTANTS (Monthly Estimates) ---
# EBS_PRICE_PER_GB  = 0.10    # Standard gp3 pricing
# IDLE_IP_PRICE     = 3.60    # ~$0.005/hr
# SNAPSHOT_PRICE    = 0.05    # Per GB/mo
# ALB_PRICE         = 16.00   # Application Load Balancer base cost

# # --- CONFIGURATION ---
# REGION = 'eu-north-1'
# SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

# def send_slack_alert(message):
#     if SLACK_WEBHOOK:
#         payload = {"text": message}
#         requests.post(SLACK_WEBHOOK, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

# def should_skip(tags):
#     """Safety Valve: Returns True if resource has a 'Skip' tag"""
#     if not tags:
#         return False
#     for tag in tags:
#         if tag['Key'] == 'Skip' and tag['Value'] == 'true':
#             return True
#     return False

# def hunt_snapshots(ec2_client):
#     print(f"--- Scanning Old Snapshots (>30 days) ---")
#     savings = 0.0
    
#     # Get snapshots owned by YOU (not public ones)
#     snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
#     # Calculate date 30 days ago
#     limit_date = datetime.now(timezone.utc) - timedelta(days=30)
    
#     for snap in snapshots:
#         if should_skip(snap.get('Tags', [])):
#             continue
            
#         # Check if snapshot is older than 30 days
#         if snap['StartTime'] < limit_date:
#             cost = snap['VolumeSize'] * SNAPSHOT_PRICE
#             msg = f"📸 *Old Snapshot*: `{snap['SnapshotId']}` ({snap['VolumeSize']}GB). Created: {snap['StartTime'].date()}. Waste: ${cost:.2f}/mo"
#             print(msg)
#             savings += cost
            
#     return savings

# def hunt_load_balancers(elbv2_client):
#     print(f"--- Scanning Idle Load Balancers ---")
#     savings = 0.0
    
#     # Get all Application Load Balancers (ALBs)
#     lbs = elbv2_client.describe_load_balancers()['LoadBalancers']
    
#     for lb in lbs:
#         # Check for tags using a separate API call (ALBs are tricky!)
#         tags = elbv2_client.describe_tags(ResourceArns=[lb['LoadBalancerArn']])['TagDescriptions'][0]['Tags']
#         if should_skip(tags):
#             continue
            
#         lb_arn = lb['LoadBalancerArn']
        
#         # Check if it has any target groups (listeners)
#         tgs = elbv2_client.describe_target_groups(LoadBalancerArn=lb_arn)['TargetGroups']
        
#         is_empty = True
#         for tg in tgs:
#             # Check health of targets in this group
#             health = elbv2_client.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']
#             if len(health) > 0:
#                 is_empty = False  # It has targets!
#                 break
        
#         if is_empty:
#             msg = f"👻 *Ghost Load Balancer*: `{lb['LoadBalancerName']}` has no active targets. Waste: ${ALB_PRICE}/mo"
#             print(msg)
#             savings += ALB_PRICE
            
#     return savings

# def hunt_elastic_ips(ec2_client):
#     print(f"--- Scanning Elastic IPs ---")
#     savings = 0.0
#     addresses = ec2_client.describe_addresses()
    
#     for addr in addresses['Addresses']:
#         if should_skip(addr.get('Tags', [])):
#             continue
            
#         if 'InstanceId' not in addr:
#             msg = f"📍 *Unused IP*: `{addr['PublicIp']}`. Waste: ${IDLE_IP_PRICE}/mo"
#             print(msg)
#             savings += IDLE_IP_PRICE
#     return savings

# def hunt_volumes(ec2_resource):
#     print(f"--- Scanning EBS Volumes ---")
#     savings = 0.0
#     for volume in ec2_resource.volumes.all():
#         if should_skip(volume.tags):
#             continue
            
#         if volume.state == 'available':
#             vol_cost = volume.size * EBS_PRICE_PER_GB
#             msg = f"💿 *Unattached Volume*: `{volume.id}` ({volume.size}GB). Waste: ${vol_cost:.2f}/mo"
#             print(msg)
#             savings += vol_cost
#     return savings

# def main():
#     # Initialize Clients
#     ec2_resource = boto3.resource('ec2', region_name=REGION)
#     ec2_client = boto3.client('ec2', region_name=REGION)
#     elbv2_client = boto3.client('elbv2', region_name=REGION) # New client for LBs
    
#     # Run all hunts
#     s_vol = hunt_volumes(ec2_resource)
#     s_ip  = hunt_elastic_ips(ec2_client)
#     s_snap = hunt_snapshots(ec2_client)
#     s_lb = hunt_load_balancers(elbv2_client)
    
#     total_savings = s_vol + s_ip + s_snap + s_lb
    
#     if total_savings > 0:
#         summary = (
#             f"💰 *FinOps Report* ({REGION})\n"
#             f"---------------------------\n"
#             f"• Volumes:   ${s_vol:.2f}\n"
#             f"• IPs:       ${s_ip:.2f}\n"
#             f"• Snapshots: ${s_snap:.2f}\n"
#             f"• LBs:       ${s_lb:.2f}\n"
#             f"---------------------------\n"
#             f"🚨 *Total Waste: ${total_savings:.2f} / mo*"
#         )
#         print(summary)
#         send_slack_alert(summary)
#     else:
#         print("✅ System Clean.")

# if __name__ == "__main__":
#     main()

import boto3
import os
import requests
import json
from datetime import datetime, timezone, timedelta

# --- PRICING CONSTANTS (Monthly Estimates) ---
EBS_PRICE_PER_GB  = 0.10    # Standard gp3 pricing
IDLE_IP_PRICE     = 3.60    # ~$0.005/hr
SNAPSHOT_PRICE    = 0.05    # Per GB/mo
ALB_PRICE         = 16.00   # Application Load Balancer base cost

# --- CONFIGURATION ---
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_alert(message):
    if SLACK_WEBHOOK:
        payload = {"text": message}
        try:
            requests.post(SLACK_WEBHOOK, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")

def should_skip(tags):
    """Safety Valve: Returns True if resource has a 'Skip' tag"""
    if not tags:
        return False
    for tag in tags:
        if tag['Key'] == 'Skip' and tag['Value'] == 'true':
            return True
    return False

def hunt_snapshots(ec2_client, region):
    # print(f"   Scanning Snapshots...") # Commented out to reduce noise
    savings = 0.0
    try:
        snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
        limit_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        for snap in snapshots:
            if should_skip(snap.get('Tags', [])):
                continue
            if snap['StartTime'] < limit_date:
                cost = snap['VolumeSize'] * SNAPSHOT_PRICE
                msg = f"📸 *{region}*: Old Snapshot `{snap['SnapshotId']}` ({snap['VolumeSize']}GB). Waste: ${cost:.2f}/mo"
                print(msg)
                savings += cost
    except Exception as e:
        print(f"Error scanning snapshots in {region}: {e}")
        
    return savings

def hunt_load_balancers(elbv2_client, region):
    # print(f"   Scanning Load Balancers...")
    savings = 0.0
    try:
        lbs = elbv2_client.describe_load_balancers()['LoadBalancers']
        for lb in lbs:
            # Tags need a separate call for LBs
            try:
                tags = elbv2_client.describe_tags(ResourceArns=[lb['LoadBalancerArn']])['TagDescriptions'][0]['Tags']
                if should_skip(tags):
                    continue
            except:
                pass # If tag fetch fails, proceed with caution or skip
                
            lb_arn = lb['LoadBalancerArn']
            tgs = elbv2_client.describe_target_groups(LoadBalancerArn=lb_arn)['TargetGroups']
            
            is_empty = True
            for tg in tgs:
                health = elbv2_client.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']
                if len(health) > 0:
                    is_empty = False
                    break
            
            if is_empty:
                msg = f"👻 *{region}*: Ghost LB `{lb['LoadBalancerName']}`. Waste: ${ALB_PRICE}/mo"
                print(msg)
                savings += ALB_PRICE
    except Exception as e:
        # Some regions might not support ELB or have permissions issues
        pass 
            
    return savings

def hunt_elastic_ips(ec2_client, region):
    savings = 0.0
    try:
        addresses = ec2_client.describe_addresses()
        for addr in addresses['Addresses']:
            if should_skip(addr.get('Tags', [])):
                continue
            if 'InstanceId' not in addr:
                msg = f"📍 *{region}*: Unused IP `{addr['PublicIp']}`. Waste: ${IDLE_IP_PRICE}/mo"
                print(msg)
                savings += IDLE_IP_PRICE
    except Exception as e:
        print(f"Error scanning IPs in {region}: {e}")
    return savings

def hunt_volumes(ec2_resource, region):
    savings = 0.0
    try:
        for volume in ec2_resource.volumes.all():
            if should_skip(volume.tags):
                continue
            if volume.state == 'available':
                vol_cost = volume.size * EBS_PRICE_PER_GB
                msg = f"💿 *{region}*: Unattached Volume `{volume.id}` ({volume.size}GB). Waste: ${vol_cost:.2f}/mo"
                print(msg)
                savings += vol_cost
    except Exception as e:
        print(f"Error scanning volumes in {region}: {e}")
    return savings

def get_active_regions():
    """Returns a list of all active AWS regions"""
    ec2 = boto3.client('ec2', region_name='us-east-1')
    response = ec2.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

def main():
    print("🚀 Starting Global FinOps Scan...")
    
    # 1. Get all regions
    try:
        regions = get_active_regions()
    except Exception as e:
        print(f"Could not fetch regions: {e}")
        regions = ['eu-north-1', 'us-east-1'] # Fallback
        
    global_savings = 0.0
    
    # 2. Loop through every region
    for region in regions:
        # print(f"--- Scanning {region} ---") # Optional: Uncomment for verbose logs
        try:
            # Initialize clients for THIS specific region
            ec2_resource = boto3.resource('ec2', region_name=region)
            ec2_client = boto3.client('ec2', region_name=region)
            elbv2_client = boto3.client('elbv2', region_name=region)
            
            # Run Hunts
            global_savings += hunt_volumes(ec2_resource, region)
            global_savings += hunt_elastic_ips(ec2_client, region)
            global_savings += hunt_snapshots(ec2_client, region)
            global_savings += hunt_load_balancers(elbv2_client, region)
            
        except Exception as e:
            # If a region is disabled or has errors, skip it
            # print(f"Skipping {region}: {e}")
            continue
            
    # 3. Final Report
    if global_savings > 0:
        summary = (
            f"💰 *Global FinOps Report*\n"
            f"---------------------------\n"
            f"🚨 *Total Monthly Waste Found: ${global_savings:.2f}*"
        )
        print(summary)
        send_slack_alert(summary)
    else:
        print("✅ Global Infrastructure Clean.")

if __name__ == "__main__":
    main()
