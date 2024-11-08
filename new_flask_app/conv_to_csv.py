import pandas as pd
import json

with open('combined_feedback_data.json') as file:
    csv_data = json.load(file)

df_csv = pd.DataFrame(csv_data)
df_csv.to_csv('sentiment_data.csv', index=False)