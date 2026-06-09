import pandas as pd
import matplotlib.pyplot as plt

filename = "AIUsage_TestData_Football.csv"
print(f"Loading {filename}...\n")

try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Could not find {filename}. Is it in the same folder?")
    exit()

print("Cleaning the data...")
df.columns = df.columns.str.strip()

if 'gross_amount' in df.columns:
    print("\n[DEBUG] Raw 'gross_amount' data (first 5 rows):")
    print(df['gross_amount'].head().apply(repr)) 
    
    clean_gross = df['gross_amount'].astype(str)
    
    clean_gross = clean_gross.str.strip()
    
    clean_gross = clean_gross.str.replace('$', '', regex=False)
    clean_gross = clean_gross.str.replace('"', '', regex=False)
    clean_gross = clean_gross.str.replace(' ', '', regex=False)
    
    clean_gross = clean_gross.str.replace(',', '.', regex=False)
    
    df['gross_amount'] = pd.to_numeric(clean_gross, errors='coerce').fillna(0)
    
    print("\n[DEBUG] Cleaned 'gross_amount' numbers (first 5 rows):")
    print(df['gross_amount'].head())
    print("-" * 40)


if 'cost_center_name' in df.columns and 'gross_amount' in df.columns:
    
    cost_per_center = df.groupby('cost_center_name')['gross_amount'].sum().sort_values(ascending=False)
    
    print("\n TOTAL COST PER COST CENTER ")
    for center_name, total_cost in cost_per_center.items():
        if pd.isna(center_name) or str(center_name).strip() == "":
            center_name = "[Unknown - Missing Cost Center]"
        
        
        #if total_cost > 0:
        print(f"{center_name}: ${total_cost:.2f}")
        if center_name == "[Unknown - Missing Cost Center]":
            print(f"{center_name}: ${total_cost:.2f}")

else:
    print("\nERROR: Couldn't find the 'cost_center_name' or 'gross_amount' columns.")



print("\nGenerating bar chart...")

plt.figure(figsize=(12, 6)) 
cost_per_center.plot(kind='bar', color='skyblue', edgecolor='black')

plt.title('Total AI Cost Per Cost Center', fontsize=16)
plt.xlabel('Cost Center (Team)', fontsize=12)
plt.ylabel('Cost ($)', fontsize=12)

plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.show()