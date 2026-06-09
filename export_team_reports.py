import pandas as pd
import os

filename = "AIUsage_TestData_Football.csv"
print(f"Loading master file: {filename}...\n")

try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Could not find {filename}.")
    exit()

df.columns = df.columns.str.strip()
if 'gross_amount' in df.columns:
    clean_gross = df['gross_amount'].astype(str)
    clean_gross = clean_gross.str.replace('$', '', regex=False).str.replace('"', '', regex=False).str.replace(' ', '', regex=False)
    clean_gross = clean_gross.str.replace(',', '.', regex=False)
    df['gross_amount'] = pd.to_numeric(clean_gross, errors='coerce').fillna(0)

output_folder = "Team_Reports"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: '{output_folder}'")

if 'cost_center_name' in df.columns:
    df['cost_center_name'] = df['cost_center_name'].fillna("Unknown_Team")
    
    all_teams = df['cost_center_name'].unique()
    
    print(f"Found {len(all_teams)} unique teams. Generating reports...\n")
    
    for team in all_teams:
        if str(team).strip() == "":
            team = "Unknown_Team"
            
        team_data = df[df['cost_center_name'] == team]
        
        team_total = team_data['gross_amount'].sum()
        
        #if team_total > 0:
            # Create a safe file name (remove spaces)
        safe_team_name = str(team).replace(' ', '_')
        export_filename = f"{output_folder}/{safe_team_name}_AI_Usage.csv"
            
            # Save the filtered data to a new CSV file
        team_data.to_csv(export_filename, index=False)
        print(f"Exported: {export_filename} (Total Cost: ${team_total:.2f})")
            
    print("\nAll reports generated successfully!")
else:
    print("Could not find the 'cost_center_name' column to group the teams.")