#!/usr/bin/env python3
"""
Deployment Dashboard - Monitor CI/CD Pipeline Status
"""

import json
import requests
import sys
from datetime import datetime
from pathlib import Path

class DeploymentDashboard:
    def __init__(self, repo_owner="fortis2a", repo_name="rev_intraday_bot"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = "https://api.github.com"
        
    def get_workflow_runs(self, workflow_name="ci-cd.yml", limit=5):
        """Get recent workflow runs"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{workflow_name}/runs"
        params = {"per_page": limit}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["workflow_runs"]
        except Exception as e:
            print(f"❌ Error fetching workflow runs: {e}")
            return []
    
    def get_deployment_status(self):
        """Get current deployment status"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/deployments"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            deployments = response.json()
            
            if deployments:
                latest = deployments[0]
                status_url = latest["statuses_url"]
                status_response = requests.get(status_url)
                statuses = status_response.json()
                
                if statuses:
                    return {
                        "environment": latest["environment"],
                        "status": statuses[0]["state"],
                        "created_at": latest["created_at"],
                        "ref": latest["ref"]
                    }
        except Exception as e:
            print(f"❌ Error fetching deployment status: {e}")
            
        return None
    
    def display_dashboard(self):
        """Display the deployment dashboard"""
        print("🏭 TRADING BOT DEPLOYMENT DASHBOARD")
        print("=" * 60)
        
        # Workflow status
        print("\n📊 Recent CI/CD Runs:")
        runs = self.get_workflow_runs()
        
        if runs:
            for run in runs[:3]:
                status_emoji = {
                    "success": "✅",
                    "failure": "❌", 
                    "in_progress": "🔄",
                    "cancelled": "⚠️"
                }.get(run["status"], "❓")
                
                created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
                print(f"  {status_emoji} {run['display_title']}")
                print(f"     Branch: {run['head_branch']} | {created.strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            print("  No recent runs found")
        
        # Deployment status
        print("\n🚀 Current Deployment:")
        deployment = self.get_deployment_status()
        
        if deployment:
            status_emoji = {
                "success": "✅",
                "failure": "❌",
                "pending": "🔄"
            }.get(deployment["status"], "❓")
            
            print(f"  {status_emoji} Environment: {deployment['environment'].upper()}")
            print(f"     Status: {deployment['status']}")
            print(f"     Branch: {deployment['ref']}")
            
            created = datetime.fromisoformat(deployment["created_at"].replace("Z", "+00:00"))
            print(f"     Deployed: {created.strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            print("  No deployments found")
        
        # Trading safety status
        print("\n⚠️  TRADING STATUS:")
        if deployment and deployment["environment"] == "production":
            print("  🔴 LIVE TRADING ACTIVE - Monitor carefully!")
        elif deployment and deployment["environment"] == "staging":
            print("  🟡 Paper trading active - Safe testing environment")
        else:
            print("  🟢 No active deployments")
        
        print("\n" + "=" * 60)
        print(f"Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main dashboard function"""
    dashboard = DeploymentDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
