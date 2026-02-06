

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
    savings = 0.0
    try:
        snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
        limit_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        for snap in snapshots:
            if should_skip(snap.get('Tags', [])):
                continue
            if snap['StartTime'] < limit_date:
                cost = snap['VolumeSize'] * SNAPSHOT_PRICE
                print(f"   📸 Old Snapshot: {snap['SnapshotId']} (${cost:.2f})")
                savings += cost
    except Exception as e:
        pass
    return savings

def hunt_load_balancers(elbv2_client, region):
    savings = 0.0
    try:
        lbs = elbv2_client.describe_load_balancers()['LoadBalancers']
        for lb in lbs:
            # Check tags first
            try:
                tags = elbv2_client.describe_tags(ResourceArns=[lb['LoadBalancerArn']])['TagDescriptions'][0]['Tags']
                if should_skip(tags): continue
            except: pass
                
            lb_arn = lb['LoadBalancerArn']
            tgs = elbv2_client.describe_target_groups(LoadBalancerArn=lb_arn)['TargetGroups']
            
            is_empty = True
            for tg in tgs:
                health = elbv2_client.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])['TargetHealthDescriptions']
                if len(health) > 0:
                    is_empty = False
                    break
            
            if is_empty:
                print(f"   👻 Ghost LB: {lb['LoadBalancerName']} (${ALB_PRICE:.2f})")
                savings += ALB_PRICE
    except:
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
                print(f"   📍 Unused IP: {addr['PublicIp']} (${IDLE_IP_PRICE:.2f})")
                savings += IDLE_IP_PRICE
    except:
        pass
    return savings

def hunt_volumes(ec2_resource, region):
    savings = 0.0
    try:
        for volume in ec2_resource.volumes.all():
            if should_skip(volume.tags):
                continue
            if volume.state == 'available':
                vol_cost = volume.size * EBS_PRICE_PER_GB
                print(f"   💿 Unattached Vol: {volume.id} (${vol_cost:.2f})")
                savings += vol_cost
    except:
        pass
    return savings

def get_active_regions():
    ec2 = boto3.client('ec2', region_name='us-east-1')
    return [region['RegionName'] for region in ec2.describe_regions()['Regions']]

def main():
    print("🚀 Starting Global FinOps Scan...")
    
    try:
        regions = get_active_regions()
    except:
        regions = ['eu-north-1', 'us-east-1'] # Fallback
        
    global_savings = 0.0
    detailed_report = []
    
    # Header for the report
    detailed_report.append("💰 *Global FinOps Report*")
    detailed_report.append("=========================")

    for region in regions:
        try:
            # print(f"Scanning {region}...") # Uncomment for debug
            ec2_res = boto3.resource('ec2', region_name=region)
            ec2_cli = boto3.client('ec2', region_name=region)
            elbv2_cli = boto3.client('elbv2', region_name=region)
            
            # Capture costs individually
            r_vol = hunt_volumes(ec2_res, region)
            r_ip = hunt_elastic_ips(ec2_cli, region)
            r_snap = hunt_snapshots(ec2_cli, region)
            r_lb = hunt_load_balancers(elbv2_cli, region)
            
            region_total = r_vol + r_ip + r_snap + r_lb
            
            # If this region has waste, add a section to the report
            if region_total > 0:
                print(f"Found ${region_total} waste in {region}") # Console log
                
                # Build the region block
                region_block = f"🌍 *{region}*: ${region_total:.2f}"
                if r_vol > 0:  region_block += f"\n     • Volumes: ${r_vol:.2f}"
                if r_ip > 0:   region_block += f"\n     • IPs: ${r_ip:.2f}"
                if r_snap > 0: region_block += f"\n     • Snapshots: ${r_snap:.2f}"
                if r_lb > 0:   region_block += f"\n     • LBs: ${r_lb:.2f}"
                
                detailed_report.append(region_block)
                global_savings += region_total
                
        except Exception as e:
            continue
            
    # Final Footer
    detailed_report.append("=========================")
    detailed_report.append(f"🚨 *Total Monthly Waste: ${global_savings:.2f}*")
    
    # Only send alert if waste was found
    if global_savings > 0:
        final_message = "\n".join(detailed_report)
        print("\n--- FINAL REPORT PREVIEW ---")
        print(final_message)
        send_slack_alert(final_message)
    else:
        print("✅ Global Infrastructure Clean.")

if __name__ == "__main__":
    main()
