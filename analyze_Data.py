import pandas as pd

filename = "AIUsage_TestData_Football.csv"
print(f"Loading {filename}...\n")

try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Could not find {filename}.")
    exit()

num_rows = len(df)
print(f"The file contains {num_rows} rows of data.\n")

if 'organization' in df.columns and 'gross_amount' in df.columns:
    cost_per_org = df.groupby('organization')['gross_amount'].sum().sort_values(ascending=False)

    print("Total per organization:")

    for org_name, total_cost in cost_per_org.items():
        if pd.isna(org_name) or str(org_name).strip():
            org_name = "[Missing Cost Center]"

        print(f"{org_name}: $")
    
    else: 
        print("The columns 'organization' or 'gross_amount' were not found in the file.")
        print("Here are the columns that actually exist in your file:", df.columns.tolist())