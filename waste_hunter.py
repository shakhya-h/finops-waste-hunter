import boto3
import os

def hunt_waste():
    # We use environment variables for security
    region = 'eun1-az1' # Change this if you created your volume in a different region
    
    ec2 = boto3.resource('ec2', region_name=region)
    print(f"--- Scanning Region: {region} ---")
    
    found_waste = False
    
    # This loop looks at every disk (volume) in your account
    for volume in ec2.volumes.all():
        # A volume is 'available' if it's NOT attached to a server
        if volume.state == 'available':
            print(f"ALERT: Unattached Volume Found!")
            print(f"ID: {volume.id} | Size: {volume.size}GB")
            found_waste = True
            
    if not found_waste:
        print("Success! No zombie volumes found.")

if __name__ == "__main__":
    hunt_waste()
