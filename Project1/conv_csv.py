import pandas as pd
import json

with open('patients.json') as file:
    csv_data = json.load(file)

df_csv = pd.DataFrame(csv_data)
df_csv.to_csv('health_data.csv', index=False)