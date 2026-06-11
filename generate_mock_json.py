import pandas as pd
import json
import os

csv_file = "AIUsage_TestData_Football.csv"
json_output_file = "mock_budgets.json"

if not os.path.exists(csv_file):
    print(f" Error: Could not find {csv_file} in this directory.")
    exit()

# 1. Read the CSV and clean up empty cost centers
df = pd.read_csv(csv_file)
if 'cost_center_name' not in df.columns:
    df['cost_center_name'] = "Default_Team"

# Fill blanks with "Unknown_Team" so the script doesn't crash
df['cost_center_name'] = df['cost_center_name'].fillna("Unknown_Team")

# Get unique Cost Centers
unique_ccs = df['cost_center_name'].unique().tolist()

print(f"🔍 Found {len(unique_ccs)} Cost Centers in the CSV.")

# 2. Build the GitHub-compliant budget structure
budgets_list = []

for cc_name in unique_ccs:
    clean_cc_name = str(cc_name).replace(' ', '_')
    manager_email = f"manager_{clean_cc_name.lower()}@alfalaval.com"
    
    # A. Find all users belonging to THIS specific cost center FIRST
    team_users = df[df['cost_center_name'] == cc_name]['username'].dropna().unique().tolist()
    print(f"   -> {cc_name}: Generating budgets for {len(team_users)} developers.")
    
    # B. Calculate the dynamic budget based on team size
    individual_cap = 150
    # Sum of all players + $200 unallocated buffer for admins to play with
    dynamic_team_budget = (len(team_users) * individual_cap) + 200 
    
    # C. Add the Cost Center Budget using the calculated amount (NO LONGER HARDCODED)
    budgets_list.append({
        "id": f"cc-{clean_cc_name.lower()}-budget",
        "target_name": cc_name,
        "budget_scope": "cost_center",
        "budget_amount": dynamic_team_budget,  
        "prevent_further_usage": True,
        "budget_alerting": {
            "will_alert": True,
            "alert_recipients": [manager_email]
        }
    })
    
    # D. Add an individual budget for each user on this team
    for user in team_users:
        budgets_list.append({
            "id": f"usr-budget-{user.lower()}",
            "target_name": user,
            "budget_scope": "user",
            "budget_amount": individual_cap,  # Individual spending cap
            "prevent_further_usage": False,
            "budget_alerting": {
                "will_alert": True,
                "alert_recipients": [manager_email, f"{user.lower()}@alfalaval.com"]
            },
            # Including the notification tracker so your pipeline script works cleanly!
            "notified_thresholds": [] 
        })

# 3. Save to mock_budgets.json
mock_json_data = {"budgets": budgets_list}

with open(json_output_file, 'w') as f:
    json.dump(mock_json_data, f, indent=2)

print(f"\n Successfully generated '{json_output_file}' with perfect dynamic math alignment!")