import pandas as pd
import json
from datetime import datetime

print("=== Fixing Amber Status Logic ===")
print(f"Timestamp: {datetime.now().isoformat()}")

# Load the current dashboard data
print("\n--- Loading Current Dashboard Data ---")
with open('dashboard_data.json', 'r') as f:
    dashboard_data = json.load(f)

materials = dashboard_data.get('room_mn_materials', [])
print(f"Total materials: {len(materials)}")

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(materials)

# Check current amber materials
current_amber = df[df['status'] == 'amber']
print(f"\nCurrent amber materials: {len(current_amber)}")
print("Sample amber materials with their consumption:")
print(current_amber[['dpn', 'description', 'balance', 'total_consumed', 'status']].head(10))

# Check how many amber materials have zero consumption
amber_no_consumption = current_amber[current_amber['total_consumed'] == 0]
print(f"\nAmber materials with zero consumption: {len(amber_no_consumption)}")
if len(amber_no_consumption) > 0:
    print("These should be green, not amber:")
    print(amber_no_consumption[['dpn', 'description', 'balance', 'total_consumed', 'status']].head(10))

# Updated status calculation - only flag as amber if balance < 10 AND has consumption
def calculate_status(row):
    balance = row['balance']
    total_consumed = row.get('total_consumed', 0)
    
    # If 0 on-hand AND 0 consumption, don't flag as red (likely inactive material)
    if balance == 0 and total_consumed == 0:
        return 'green'
    elif balance == 0:
        return 'red'
    elif balance < 10 and total_consumed > 0:
        return 'amber'  # Only amber if low stock AND has consumption
    else:
        return 'green'

# Apply the updated status calculation
df['status'] = df.apply(calculate_status, axis=1)

# Recalculate zero_stock_flag
df['zero_stock_flag'] = (df['balance'] == 0) & (df['total_consumed'] > 0)

# Check the changes
new_amber = df[df['status'] == 'amber']
print(f"\nNew amber materials: {len(new_amber)}")
print("Materials that changed from amber to green:")
changed_to_green = current_amber[current_amber['dpn'].isin(df[df['status'] == 'green']['dpn'])]
print(f"Count: {len(changed_to_green)}")
if len(changed_to_green) > 0:
    print(changed_to_green[['dpn', 'description', 'balance', 'total_consumed']].head(10))

# Count status changes
status_counts = df['status'].value_counts()
print(f"\nNew status distribution:")
print(status_counts)

# Update the dashboard data
dashboard_data['room_mn_materials'] = df.to_dict(orient='records')
dashboard_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update summary
summary = {
    'total_materials': len(df),
    'red_status': len(df[df['status'] == 'red']),
    'amber_status': len(df[df['status'] == 'amber']),
    'green_status': len(df[df['status'] == 'green']),
    'zero_stock_consumed': len(df[df['zero_stock_flag'] == True]),
    'q1_consumption': df['q1_consumption'].sum(),
    'q2_consumption': df['q2_consumption'].sum(),
    'q3_consumption': df['q3_consumption'].sum(),
    'q3_projected': df['q3_projected'].sum(),
    'total_consumed': df['total_consumed'].sum(),
    'cork_materials': int(df['in_cork_list'].sum()),
    'materials_with_q3_projections': int((df['q3_projected'] > 0).sum()),
    'materials_from_balsheet': int((df['balance'] > 0).sum()),
    'analysis_date': datetime.now().isoformat(),
    'data_source': 'Material-Cork tab + Material Reference descriptions + BALSHEET 8th Sep quantities + Quarterly Movements + Q3 Build Projections (Fixed amber logic: only flag if low stock AND consumption)'
}

dashboard_data['material_summary'] = summary

print(f"\n=== Updated Analysis Summary ===")
print(f"Total Materials: {summary['total_materials']}")
print(f"Red Status: {summary['red_status']}")
print(f"Amber Status: {summary['amber_status']}")
print(f"Green Status: {summary['green_status']}")
print(f"Zero Stock (Consumed): {summary['zero_stock_consumed']}")

# Save updated dashboard data
print("\n--- Saving Updated Dashboard Data ---")
with open('dashboard_data.json', 'w') as f:
    json.dump(dashboard_data, f, indent=2, default=str)

print("Dashboard data updated successfully")

# Generate embedded data file
print("\n--- Generating Embedded Data File ---")
embedded_data = f"const dashboardData = {json.dumps(dashboard_data, indent=2, default=str)};"

with open('embedded_dashboard_data.js', 'w') as f:
    f.write(embedded_data)

print("Embedded data file generated successfully")

print("\n=== Amber Status Logic Fix Complete ===")
print("Materials with low stock but no consumption are now green, not amber")