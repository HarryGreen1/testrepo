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

if not os.path.exists(csv_file) or not os.path.exists(json_file):
    print("Error: Missing either the CSV usage file or the JSON budget file.")
    exit()

print("Loading Usage and Budget Data...\n")
df_usage = pd.read_csv(csv_file)
df_usage['gross_amount'] = clean_gross_amount(df_usage['gross_amount'])

with open(json_file, 'r') as f:
    budget_data = json.load(f)

user_spend = df_usage.groupby('username')['gross_amount'].sum().to_dict()

print("RUNNING USER THRESHOLD CHECKS")

for budget in budget_data.get('budgets', []):
    
    if budget['budget_scope'] == 'user':
        username = budget['target_name']
        limit = budget['budget_amount']
        
        actual_spend = user_spend.get(username, 0)
        
        if limit > 0:
            usage_percent = (actual_spend / limit) * 100
        else:
            usage_percent = 0


        threshold_crossed = None
        if usage_percent >= 90:
            threshold_crossed = "90%"
        elif usage_percent >= 75:
            threshold_crossed = "75%"
        elif usage_percent >= 50:
            threshold_crossed = "50%"

        if threshold_crossed and budget['budget_alerting']['will_alert']:
            recipients = ", ".join(budget['budget_alerting']['alert_recipients'])
            print(f" MOCK EMAIL SENT TO: {recipients}")
            print(f" Subject: ALERT: {username} has crossed {threshold_crossed} of their AI Budget!")
            print(f" Details: Spent ${actual_spend:.2f} out of ${limit:.2f} limit ({usage_percent:.1f}%)\n")
        else:
            print(f"{username} is in good standing. ({usage_percent:.1f}% used of ${limit:.2f})\n")

print(f"\nCheck complete.")