import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib

matplotlib.use('Agg') 

folder_name = "Team_Reports"
if not os.path.exists(folder_name):
    print(f"Error: Could not find the '{folder_name}' folder. Run export_team_reports.py first!")
    exit()

files = os.listdir(folder_name)
csv_files = [f for f in files if f.endswith('.csv')]

print(f"Found {len(csv_files)} team reports. Generating charts...")

for file in csv_files:
    team_name = file.replace('_AI_Usage.csv', '')
    file_path = f"{folder_name}/{file}"
    
    df = pd.read_csv(file_path)
    
    if 'username' in df.columns and 'gross_amount' in df.columns:
        cost_per_user = df.groupby('username')['gross_amount'].sum().sort_values(ascending=False)
        cost_per_user = cost_per_user[cost_per_user > 0]
        
        if not cost_per_user.empty:
            plt.figure(figsize=(10, 6))
            cost_per_user.plot(kind='bar', color='coral', edgecolor='black')
            
            plt.title(f'AI Cost Breakdown by User: {team_name.replace("_", " ")}', fontsize=16)
            plt.xlabel('Developer / User', fontsize=12)
            plt.ylabel('Total Cost ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            image_path = f"{folder_name}/{team_name}_Chart.png"
            plt.savefig(image_path)
            
            plt.close()

print("\nAll charts generated successfully!")