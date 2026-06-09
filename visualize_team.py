import pandas as pd
import matplotlib.pyplot as plt
import os

print("TEAM REPORT VISUALIZER")
print("Example teams: Napoli, Real Madrid, Juventus, Liverpool\n")

team_name = input("Enter the name of the team you want to visualize: ")

safe_team_name = team_name.replace(' ', '_')
filename = f"Team_Reports/{safe_team_name}_AI_Usage.csv"

if not os.path.exists(filename):
    print(f"\n ERROR: Could not find a report for '{team_name}'.")
    print("Check the 'Team_Reports' for spelling.")
    exit()

print(f"\nLoading data for {team_name}...")
df = pd.read_csv(filename)

if 'username' in df.columns and 'gross_amount' in df.columns:
    cost_per_user = df.groupby('username')['gross_amount'].sum().sort_values(ascending=False)
    
    #cost_per_user = cost_per_user[cost_per_user > 0]
    
    if cost_per_user.empty:
        print(f"No active spending found for users in {team_name}.")
        exit()

    print("Generating graph... (Close the graph window to exit the program)")
    
    plt.figure(figsize=(10, 6))
    cost_per_user.plot(kind='bar', color='coral', edgecolor='black')
    
    plt.title(f'AI Cost Breakdown by User: {team_name}', fontsize=16)
    plt.xlabel('Developer / User', fontsize=12)
    plt.ylabel('Total Cost ($)', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()

else:
    print("\n ERROR: The file is missing the 'username' or 'gross_amount' column.")