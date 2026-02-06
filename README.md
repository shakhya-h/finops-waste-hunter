# 🌍 Global FinOps Waste Hunter

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20ELB-orange?style=flat&logo=amazon-aws&logoColor=white)
![Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black?style=flat&logo=github&logoColor=white)

> **Automated cloud governance tool that detects, quantifies, and reports "zombie" infrastructure across all AWS regions.**

## ⚡ The Problem vs. Solution
| The Pain 📉 | The Solution 🛡️ |
| :--- | :--- |
| **Hidden Costs:** Forgotten IPs & disks cost $100s/mo. | **Auto-Discovery:** Scans orphan resources globally. |
| **Manual Audits:** Checking 15 regions takes hours. | **Zero-Touch:** Runs weekly via GitHub Actions. |
| **Bill Shock:** No visibility until the invoice arrives. | **Instant Alerts:** Real-time Slack notifications with $$$ impact. |

## 🎯 What it Hunts
| Resource | Condition | Cost Estimate |
| :--- | :--- | :--- |
| **EBS Volumes** | Available / Unattached | ~$0.10 / GB |
| **Load Balancers** | 0 Healthy Targets | ~$16.00 / mo |
| **Elastic IPs** | Unassociated | ~$3.60 / mo |
| **Snapshots** | Created > 30 days ago | ~$0.05 / GB |

## 📸 Sample Output (Slack)
The bot sends an itemized receipt to your engineering channel:

```text
💰 Global FinOps Report
=========================
🌍 eu-north-1: $20.25
     • Volumes: $0.10 (1GB orphaned disk)
     • LBs: $16.50 (Idle Load Balancer)
     • IPs: $3.60 (Unused Static IP)

🌍 us-east-1: $5.00
     • Snapshots: $5.00 (100GB old backup)
=========================
🚨 Total Monthly Waste: $25.25
```
## **🚀 Quick Start**
1. **Clone & Install**
     Bash
   
     git clone [https://github.com/shakhya-h/finops-waste-hunter.git](https://github.com/shakhya-h/finops-waste-hunter.git)
   
     cd finops-waste-hunter
   
     pip install boto3 requests

3. **Configure AWS**
     Bash
   
     export AWS_ACCESS_KEY_ID="your_key"
   
     export AWS_SECRET_ACCESS_KEY="your_secret"
   
     export SLACK_WEBHOOK_URL="your_webhook"

5. **Run the Hunter**
     Bash
   
     python waste_hunter.py
   
## **⚙️ Architecture**
     Core: Python script uses boto3 to loop through all active AWS regions (describe_regions).
     
     Logic: Aggregates costs per region and filters out resources tagged Skip=True.
     
     CI/CD: cron job on GitHub Actions triggers the scan every Sunday at 00:00 UTC.

**Shakhya Halder,2026**
