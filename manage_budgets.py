import pandas as pd
import json
import os

csv_file = "AIUsage_TestData_Football.csv"
json_file = "mock_budgets.json"

def clean_gross_amount(series):
    clean_series = series.astype(str).str.strip()
    clean_series = clean_series.str.replace('$', '', regex=False).str.replace('"', '', regex=False).str.replace(' ', '', regex=False)
    clean_series = clean_series.str.replace(',', '.', regex=False)
    return pd.to_numeric(clean_series, errors='coerce').fillna(0)

def update_user_budget_team_balanced(target_user, new_limit, cost_center_name):
    print(f"\nAdmin Request: Change {target_user}'s limit to ${new_limit} inside Cost Center '{cost_center_name}'...")
    
    if not os.path.exists(json_file):
        print("Error: Budget configuration file not found.")
        return

    if not os.path.exists(csv_file):
        print("Error: Usage data file not found. Cannot validate spending constraints.")
        return

    # Load usage data to get everyone's current spend for the watermark constraint
    df_usage = pd.read_csv(csv_file)
    df_usage['gross_amount'] = clean_gross_amount(df_usage['gross_amount'])
    user_spend = df_usage.groupby('username')['gross_amount'].sum().to_dict()

    with open(json_file, 'r') as f:
        data = json.load(f)
        
    budgets = data.get('budgets', [])
    
    target_item = None
    team_members = []
    
    clean_cc_name = str(cost_center_name).replace(' ', '_').lower()
    expected_manager = f"manager_{clean_cc_name}@alfalaval.com"
    
    for b in budgets:
        if b['budget_scope'] == 'user':
            if b['budget_alerting']['alert_recipients'][0] == expected_manager:
                if b['target_name'] == target_user:
                    target_item = b
                else:
                    team_members.append(b) 

    if not target_item:
        print(f"Modification Blocked: Could not find '{target_user}' inside Cost Center '{cost_center_name}'.")
        return

    cc_budget_exists = False
    for b in budgets:
        if b['budget_scope'] == 'cost_center' and b['target_name'] == cost_center_name:
            if b['budget_amount'] > 0:
                cc_budget_exists = True
                break

    if not cc_budget_exists:
        print(f"CONSTRAINT VIOLATION: Cost Center '{cost_center_name}' has no defined budget allocation.")
        return

    current_target_limit = target_item['budget_amount']
    difference = new_limit - current_target_limit 
    if difference == 0:
        print("Info: No change in budget amount requested.")
        return
        
    if not team_members:
        print("Error: No other team members exist to absorb or receive the balanced budget shift.")
        return

    split_share = difference / len(team_members)
    
    if difference > 0: 
        for member in team_members:
            proposed_budget = member['budget_amount'] - split_share
            current_spend = user_spend.get(member['target_name'], 0)
            
            if proposed_budget < 0 or proposed_budget < current_spend:
                print("CONSTRAINT VIOLATION: Transaction rolled back.")
                print(f"   Cannot reduce {member['target_name']}'s budget to ${proposed_budget:.2f}.")
                print(f"   They have already spent ${current_spend:.2f} this month.")
                return

    target_item['budget_amount'] = new_limit
    for member in team_members:
        member['budget_amount'] = round(member['budget_amount'] - split_share, 2)
        
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    print("Success! Distributed Zero-Sum modification saved.")
    print(f"   -> {target_user} limit shifted from ${current_target_limit} to ${new_limit}")
    print(f"   -> The remaining ${difference} adjustment was split across {len(team_members)} team members (${split_share:.2f} each).")

def run_pipeline():
    if not os.path.exists(csv_file) or not os.path.exists(json_file):
        print("Error: Missing database files.")
        return

    print("Loading Usage and Budget Data...")
    df_usage = pd.read_csv(csv_file)
    df_usage['gross_amount'] = clean_gross_amount(df_usage['gross_amount'])
    
    with open(json_file, 'r') as f:
        budget_data = json.load(f)

    user_spend = df_usage.groupby('username')['gross_amount'].sum().to_dict()

    state_updated = False

    for budget in budget_data.get('budgets', []):
        if budget['budget_scope'] == 'user':
            username = budget['target_name']
            limit = budget['budget_amount']
            actual_spend = user_spend.get(username, 0)
            
            usage_percent = (actual_spend / limit) * 100 if limit > 0 else 0

            if 'notified_thresholds' not in budget:
                budget['notified_thresholds'] = []

            current_tier = None
            if usage_percent >= 90: current_tier = 90
            elif usage_percent >= 75: current_tier = 75
            elif usage_percent >= 50: current_tier = 50

            if current_tier and budget['budget_alerting']['will_alert']:
                if current_tier not in budget['notified_thresholds']:
                    recipients = ", ".join(budget['budget_alerting']['alert_recipients'])
                    print(f"ALERT [{current_tier}%] -> Emails sent to: {recipients}")
                    print(f"{username} spent ${actual_spend:.2f} / ${limit:.2f} ({usage_percent:.1f}%)")
                    
                    budget['notified_thresholds'].append(current_tier)
                    state_updated = True
                    
    if state_updated:
        with open(json_file, 'w') as f:
            json.dump(budget_data, f, indent=2)

if __name__ == "__main__":

    target = os.getenv("TARGET_USER")
    new_limit_str = os.getenv("NEW_LIMIT")
    cc_name = os.getenv("COST_CENTER")

    if target and new_limit_str and cc_name:
        try:
            update_user_budget_team_balanced(target, float(new_limit_str), cc_name)
        except ValueError:
            print("Error: New limit must be a number.")

    run_pipeline()
    print("Done!")