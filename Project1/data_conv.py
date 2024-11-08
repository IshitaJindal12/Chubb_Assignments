import pandas as pd
import json
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

patient_data = []

# Sample data
first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Grace', 'Helen', 'Ivy']
last_names = ['Smith', 'Jones', 'Taylor', 'Brown', 'Williams', 'Davis', 'Miller', 'Wilson', 'Moore', 'Anderson']
locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'Austin']
moods = ['happy', 'anxious', 'sad', 'excited', 'angry', 'calm', 'stressed', 'relaxed']

# Generate 100 records
for i in range(1, 101):
    user_id = i  # Unique user_id, starting from 10001
    first_name = first_names[i % len(first_names)]
    last_name = last_names[i % len(last_names)]
    age = 18 + (i % 50)  # Random age between 18 and 67
    gender = 'male' if i % 2 == 0 else 'female'
    location = locations[i % len(locations)]
    
    date_recorded = (datetime.now() - timedelta(days=i * 3)).strftime('%Y-%m-%d')
    
    weight_kg = 50 + (i % 30)  # Random weight between 50 and 80 kg
    height_cm = 150 + (i % 30)  # Random height between 150 and 180 cm
    bmi = weight_kg / (height_cm / 100) ** 2
    heart_rate_bpm = 60 + (i % 40)  # Random heart rate between 60 and 100 bpm
    bp_systolic = 100 + (i % 20)  # Random systolic blood pressure between 100 and 120
    bp_diastolic = 60 + (i % 10)  # Random diastolic blood pressure between 60 and 70
    steps_count = 1000 + (i * 10)  # Random steps count, increasing with each entry
    calories_burned = 200 + (i * 5)  # Random calories burned
    sleep_duration_hours = 7 + (i % 3)  # Random sleep hours between 7 and 9
    sleep_quality = i % 5  # Random sleep quality (0-4)
    mood = moods[i % len(moods)]
    stress_level = 1 + (i % 5)  # Stress level between 1 and 5
    water_intake_liters = 1 + (i % 4)  # Random water intake between 1 and 4 liters
    
    patient_data.append({
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'age': age,
        'gender': gender,
        'location': location,
        'date_recorded': date_recorded,
        'weight_kg': weight_kg,
        'height_cm': height_cm,
        'bmi': round(bmi, 2),
        'heart_rate_bpm': heart_rate_bpm,
        'bp_systolic': bp_systolic,
        'bp_diastolic': bp_diastolic,
        'steps_count': steps_count,
        'calories_burned': calories_burned,
        'sleep_duration_hours': sleep_duration_hours,
        'sleep_quality': sleep_quality,
        'mood': mood,
        'stress_level': stress_level,
        'water_intake_liters': water_intake_liters
    })

import pandas as pd
import json
import xml.etree.ElementTree as ET

# Load JSON data
with open('patients.json') as file:
    data = json.load(file)

# Split data into chunks of 20
json_data = data[:20]
csv_data = data[20:40]
xml_data = data[40:60]
excel_data = data[60:80]
html_data = data[80:100]

# Convert JSON data to CSV
df_csv = pd.DataFrame(csv_data)
df_csv.to_csv('patients.csv', index=False)

# Convert JSON data to XML
root = ET.Element('Patients')
for entry in xml_data:
    patient = ET.SubElement(root, 'Patient')
    for key, value in entry.items():
        ET.SubElement(patient, key).text = str(value)
tree = ET.ElementTree(root)
tree.write('patients.xml')

# Convert JSON data to Excel
df_excel = pd.DataFrame(excel_data)
df_excel.to_excel('patients.xlsx', index=False)

# Convert JSON data to HTML
df_html = pd.DataFrame(html_data)
df_html.to_html('patients.html', index=False)

# Save the first 20 data in JSON format
with open('patients_json.json', 'w') as file:
    json.dump(json_data, file, indent=4)