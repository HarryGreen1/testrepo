import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
import shutil # <--- NEW: Python's built-in file mover

matplotlib.use('Agg') 

folder_name = "Team_Reports"
if not os.path.exists(folder_name):
    print(f"Error: Could not find the '{folder_name}' folder. Run export_team_reports.py first!")
    exit()

master_file = "AIUsage_TestData_Football.csv"
if os.path.exists(master_file):
    print("Generating Master Organization Chart...")
    df_master = pd.read_csv(master_file)
    
    df_master.columns = df_master.columns.str.strip()
    if 'gross_amount' in df_master.columns and 'cost_center_name' in df_master.columns:
        clean_gross = df_master['gross_amount'].astype(str)
        clean_gross = clean_gross.str.replace('$', '', regex=False).str.replace('"', '', regex=False).str.replace(' ', '', regex=False)
        clean_gross = clean_gross.str.replace(',', '.', regex=False)
        df_master['gross_amount'] = pd.to_numeric(clean_gross, errors='coerce').fillna(0)
        
        df_master['cost_center_name'] = df_master['cost_center_name'].fillna("Unknown_Team")
        cost_per_center = df_master.groupby('cost_center_name')['gross_amount'].sum().sort_values(ascending=False)
        cost_per_center = cost_per_center[cost_per_center > 0]
        
        if not cost_per_center.empty:
            plt.figure(figsize=(12, 6))
            cost_per_center.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title('Total AI Cost Per Team (Entire Organization)', fontsize=16)
            plt.xlabel('Cost Center (Team)', fontsize=12)
            plt.ylabel('Total Cost ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            master_chart_path = f"{folder_name}/00_Master_Org_Chart.png"
            plt.savefig(master_chart_path)
            plt.close()
            print(f"Saved Master Chart: {master_chart_path}\n")

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

print("\nConverting to Executive Excel Reports...")

for file in csv_files:
    team_name = file.replace('_AI_Usage.csv', '')
    csv_path = f"{folder_name}/{file}"
    png_path = f"{folder_name}/{team_name}_Chart.png"
    excel_path = f"{folder_name}/{team_name}_Executive_Report.xlsx"
    
    df_excel = pd.read_csv(csv_path)
    
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    df_excel.to_excel(writer, sheet_name='AI Usage Data', index=False)
    
    workbook  = writer.book
    worksheet = writer.sheets['AI Usage Data']
    
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    
    for col_num, value in enumerate(df_excel.columns):
        worksheet.write(0, col_num, value, header_format)
    
    worksheet.set_column(0, len(df_excel.columns) - 1, 18)
    
    if 'gross_amount' in df_excel.columns:
        col_idx = df_excel.columns.get_loc('gross_amount')
        worksheet.set_column(col_idx, col_idx, 18, currency_format)

    image_start_cell = f"A{len(df_excel) + 3}"

    if os.path.exists(png_path):
        worksheet.insert_image(image_start_cell, png_path, {'x_scale': 0.8, 'y_scale': 0.8})
    
    writer.close()

print("\nAll Executive Excel reports are ready!")

print("\nCleaning up and organizing the Team_Reports folder...")

csv_dir = f"{folder_name}/Raw_CSVs"
chart_dir = f"{folder_name}/Charts"
excel_dir = f"{folder_name}/Final_Excel_Reports"

os.makedirs(csv_dir, exist_ok=True)
os.makedirs(chart_dir, exist_ok=True)
os.makedirs(excel_dir, exist_ok=True)

for file in os.listdir(folder_name):
    file_path = f"{folder_name}/{file}"
    
    if os.path.isdir(file_path):
        continue
        
    if file.endswith('.csv'):
        os.replace(file_path, f"{csv_dir}/{file}")
    elif file.endswith('.png'):
        os.replace(file_path, f"{chart_dir}/{file}")
    elif file.endswith('.xlsx'):
        os.replace(file_path, f"{excel_dir}/{file}")

print("Folder cleanup complete!")