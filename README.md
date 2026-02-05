# 🚀 FinOps Waste Hunter (AWS)

A Python-based automation tool that identifies unattached EBS volumes (zombie resources) across AWS regions to reduce cloud spend.

## 📈 The Business Problem
Cloud infrastructure often suffers from "resource leakage" where storage volumes remain active after their parent instances are terminated. For a mid-sized company, these orphaned volumes can easily cost **$500–$1,000/month** in unnecessary billing.

## 🛠️ Tech Stack & Skills
* **Language:** Python (Boto3 SDK)
* **Cloud:** AWS (EC2, IAM)
* **Automation:** GitHub Actions (CI/CD)
* **Observability:** Slack API Integration

## ⚙️ How it Works
1.  **Scanner:** A Python script queries the AWS EC2 API to find volumes in the `available` state.
2.  **Automation:** GitHub Actions runs the script on a weekly `cron` schedule.
3.  **Alerting:** If waste is found, an actionable alert is sent to a Slack channel via Webhooks.



## 💡 Impact Realized
* **Cost Reduction:** Automates the discovery of resources that cost ~$0.10 per GB/month.
* **Efficiency:** Replaces manual infrastructure audits with 100% automated reporting.
* **Security:** Implements "Least Privilege" access using AWS IAM policies.

---
*Created by Shakhya Halder.*
