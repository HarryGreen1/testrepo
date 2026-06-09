import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
import shutil

matplotlib.use('Agg') 

folder_name = "Team_Reports"
master_file = "AIUsage_TestData_Football.csv"
model_column_name = 'model'
os.makedirs(folder_name, exist_ok=True)

def clean_gross_amount(series):
    clean_series = series.astype(str).str.strip()
    clean_series = clean_series.str.replace('$', '', regex=False).str.replace('"', '', regex=False).str.replace(' ', '', regex=False)
    clean_series = clean_series.str.replace(',', '.', regex=False)
    return pd.to_numeric(clean_series, errors='coerce').fillna(0)

print("1. Generating Per-Team CSVs from Master Dat")
if os.path.exists(master_file):
    df_master_source = pd.read_csv(master_file)
    df_master_source.columns = df_master_source.columns.str.strip()
    
    if 'cost_center_name' in df_master_source.columns:
        df_master_source['cost_center_name'] = df_master_source['cost_center_name'].fillna("Unknown_Team")
        unique_teams = df_master_source['cost_center_name'].unique()
        
        for team in unique_teams:
            if not str(team).strip():
                continue
            team_data = df_master_source[df_master_source['cost_center_name'] == team].copy()
            if 'gross_amount' in team_data.columns:
                team_data['gross_amount'] = clean_gross_amount(team_data['gross_amount'])
            
            safe_team_name = str(team).replace(' ', '_').strip()
            team_report_path = os.path.join(folder_name, f"{safe_team_name}_AI_Usage.csv")
            team_data.to_csv(team_report_path, index=False)
    else:
        print("Error: 'cost_center_name' missing from master file.")
else:
    print(f"Error: Master file '{master_file}' not found. Cannot split data.")
    exit()

print("\n2. Generating Master Organization Chart")
df_master_vis = pd.read_csv(master_file)
df_master_vis.columns = df_master_vis.columns.str.strip()

if 'gross_amount' in df_master_vis.columns and 'cost_center_name' in df_master_vis.columns:
    df_master_vis['gross_amount'] = clean_gross_amount(df_master_vis['gross_amount'])
    df_master_vis['cost_center_name'] = df_master_vis['cost_center_name'].fillna("Unknown_Team")
    
    cost_per_center = df_master_vis.groupby('cost_center_name')['gross_amount'].sum().sort_values(ascending=False)
    cost_per_center = cost_per_center[cost_per_center > 0]
    
    if not cost_per_center.empty:
        plt.figure(figsize=(12, 6))
        cost_per_center.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Total AI Cost Per Team (Entire Organization)', fontsize=16)
        plt.xlabel('Cost Center (Team)', fontsize=12)
        plt.ylabel('Total Cost ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        master_chart_path = os.path.join(folder_name, "00_Master_Org_Chart.png")
        plt.savefig(master_chart_path)
        plt.close()
        print(f"Saved Master Chart: {master_chart_path}")

print("\n3. Generating Individual Team Stacked Charts")
files = os.listdir(folder_name)
csv_files = [f for f in files if f.endswith('_AI_Usage.csv')]

for file in csv_files:
    team_name = file.replace('_AI_Usage.csv', '')
    file_path = os.path.join(folder_name, file)
    
    df_team = pd.read_csv(file_path)
    
    if 'username' in df_team.columns and 'gross_amount' in df_team.columns and model_column_name in df_team.columns:
        
        cost_per_user_model = df_team.groupby(['username', model_column_name])['gross_amount'].sum().unstack().fillna(0)
        cost_per_user_model['Total_Spend'] = cost_per_user_model.sum(axis=1)
        cost_per_user_model = cost_per_user_model[cost_per_user_model['Total_Spend'] > 0]
        cost_per_user_model = cost_per_user_model.sort_values(by='Total_Spend', ascending=False).drop(columns='Total_Spend')
        
        if not cost_per_user_model.empty:
            plt.figure(figsize=(10, 6))
            cost_per_user_model.plot(kind='bar', stacked=True, edgecolor='black', colormap='tab20', ax=plt.gca())
            
            plt.title(f'AI Cost Breakdown by User & Model: {team_name.replace("_", " ")}', fontsize=16)
            plt.xlabel('Developer / User', fontsize=12)
            plt.ylabel('Total Cost ($)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.legend(title='AI Model', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            
            image_path = os.path.join(folder_name, f"{team_name}_Chart.png")
            plt.savefig(image_path)
            plt.close()

print("\n4. Converting to Executive Excel Pivot Reports")
for file in csv_files:
    team_name = file.replace('_AI_Usage.csv', '')
    csv_path = os.path.join(folder_name, file)
    png_path = os.path.join(folder_name, f"{team_name}_Chart.png")
    excel_path = os.path.join(folder_name, f"{team_name}_Executive_Report.xlsx")
    
    df_raw = pd.read_csv(csv_path)
    
    if 'username' in df_raw.columns and 'gross_amount' in df_raw.columns and model_column_name in df_raw.columns:
        
        df_excel = df_raw.pivot_table(index='username', columns=model_column_name, values='gross_amount', aggfunc='sum', fill_value=0)
        df_excel['Total Spend'] = df_excel.sum(axis=1)
        df_excel = df_excel.sort_values(by='Total Spend', ascending=False).reset_index()
    else:
        df_excel = df_raw 

    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    df_excel.to_excel(writer, sheet_name='AI Usage Data', index=False)
    
    workbook  = writer.book
    worksheet = writer.sheets['AI Usage Data']
    
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    
    for col_num, value in enumerate(df_excel.columns):
        worksheet.write(0, col_num, value, header_format)
    
    worksheet.set_column(0, len(df_excel.columns) - 1, 18)
    
    for col_num, col_name in enumerate(df_excel.columns):
        if col_name != 'username':
            worksheet.set_column(col_num, col_num, 18, currency_format)

    image_start_cell = f"A{len(df_excel) + 3}"
    if os.path.exists(png_path):
        worksheet.insert_image(image_start_cell, png_path, {'x_scale': 0.8, 'y_scale': 0.8})
    
    writer.close()

print("\n5. Cleaning up and organizing the Team_Reports folder")
csv_dir = os.path.join(folder_name, "Raw_CSVs")
chart_dir = os.path.join(folder_name, "Charts")
excel_dir = os.path.join(folder_name, "Final_Excel_Reports")

os.makedirs(csv_dir, exist_ok=True)
os.makedirs(chart_dir, exist_ok=True)
os.makedirs(excel_dir, exist_ok=True)

for file in os.listdir(folder_name):
    file_path = os.path.join(folder_name, file)
    
    if os.path.isdir(file_path):
        continue
        
    if file.endswith('.csv'):
        os.replace(file_path, os.path.join(csv_dir, file))
    elif file.endswith('.png'):
        os.replace(file_path, os.path.join(chart_dir, file))
    elif file.endswith('.xlsx'):
        os.replace(file_path, os.path.join(excel_dir, file))

print("Pipeline complete! All files organized securely.")