import pandas as pd
import requests
import os

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "X-GitHub-Api-Version": "2026-03-10"
}

url = "https://api.github.com/organizations/FutbolCorp/settings/billing/ai_credit/usage"
response = requests.get(url, headers=headers)
response.raise_for_status()
data = response.json()

csv_rows = []

for item in data.get('usageItems', []):
    row = {
        "date": item.get('date'),
        "username": item.get('user', 'unknown'),
        "product": "copilot",
        "sku": item.get('sku', 'copilot_ai_credit'),
        "model": item.get('model'),
        "quantity": item.get('grossQuantity'),
        "unit_type": "ai-credits",
        "applied_cost_per_quantity": item.get('pricePerUnit'),
        "gross_amount": item.get('grossAmount', 0),
        "discount_amount": item.get('discountAmount', 0),
        "net_amount": item.get('netAmount', 0),
        "organization": "FutbolCorp",
        "repository": item.get('repository', ''),
        "cost_center_name": item.get('costCenter', 'Unknown_Team'),
        "aic_quantity": item.get('grossQuantity'),
        "aic_gross_amount": item.get('grossAmount')
    }
    csv_rows.append(row)

df = pd.DataFrame(csv_rows)
df.to_csv("AIUsage_TestData_Football.csv", index=False, quoting=1)

os.makedirs("Team_Reports", exist_ok=True)
for team_name, team_data in df.groupby("cost_center_name"):
    safe_name = str(team_name).replace(" ", "_").replace("/", "-")
    file_path = f"Team_Reports/{safe_name}_Usage_Report.csv"
    team_data.to_csv(file_path, index=False, quoting=1)