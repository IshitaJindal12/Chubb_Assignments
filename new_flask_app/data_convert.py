import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

sources = ["social media", "survey", "review site"]
sentiment_categories = ["positive", "neutral", "negative"]
keywords_list = ["service", "quality", "response", "delivery", "pricing", "recommend"]
roles = ["admin", "viewer"]

feedback_data = []

for i in range(1, 101):
    feedback_id = i
    sentiment_id = i
    metric_id = i
    user_id = (i % 50) + 1

    source = sources[i % len(sources)]
    content = f"Sample feedback content {i}"
    sentiment_score = round(0.5 + (i % 10) * 0.05, 2)
    sentiment_category = sentiment_categories[i % len(sentiment_categories)]
    keywords = keywords_list[i % len(keywords_list)]
    timestamp = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
    analysis_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    email = f"user{user_id}@example.com"
    time_period = "monthly"

    total_feedback = 20 + (i % 80)
    positive_feedback_count = (i % 15) + 5
    neutral_feedback_count = (i % 10) + 5
    negative_feedback_count = (i % 8) + 5
    average_sentiment_score = round(0.4 + (i % 6) * 0.1, 2)

    feedback_data.append({
        'feedback_id': feedback_id,
        'sentiment_id': sentiment_id,
        'metric_id': metric_id,
        'source': source,
        'content': content,
        'sentiment_score': sentiment_score,
        'sentiment_category': sentiment_category,
        'keywords': keywords,
        'timestamp': timestamp,
        'analysis_date': analysis_date,
        'user_id': user_id,
        'email': email,
        'time_period': time_period,
        'total_feedback': total_feedback,
        'positive_feedback_count': positive_feedback_count,
        'neutral_feedback_count': neutral_feedback_count,
        'negative_feedback_count': negative_feedback_count,
        'average_sentiment_score': average_sentiment_score
    })

json_data = feedback_data[:20]
csv_data = feedback_data[20:40]
xml_data = feedback_data[40:60]
excel_data = feedback_data[60:80]
html_data = feedback_data[80:100]

with open('feedback_data.json', 'w') as file:
    json.dump(json_data, file, indent=4)

df_csv = pd.DataFrame(csv_data)
df_csv.to_csv('feedback_data.csv', index=False)

root = ET.Element('FeedbackData')
for entry in xml_data:
    feedback_entry = ET.SubElement(root, 'FeedbackEntry')
    for key, value in entry.items():
        ET.SubElement(feedback_entry, key).text = str(value)
tree = ET.ElementTree(root)
tree.write('feedback_data.xml')

df_excel = pd.DataFrame(excel_data)
df_excel.to_excel('feedback_data.xlsx', index=False)

df_html = pd.DataFrame(html_data)
df_html.to_html('feedback_data.html', index=False)