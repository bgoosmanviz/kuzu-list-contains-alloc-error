# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "kuzu",
#     "rich",
# ]
# ///
import json
import os
import random
import kuzu
from rich import print
from datetime import datetime, timedelta
import uuid

# List of 10 random names
names = [
    "Alice Johnson",
    "Bob Smith",
    "Carol White",
    "David Brown",
    "Emma Davis",
    "Frank Miller",
    "Grace Wilson",
    "Henry Taylor",
    "Ivy Martinez",
    "Jack Anderson"
]

# List of sample email headers
sample_headers = [
    "From: sender@example.com\nTo: recipient@example.com\nSubject: Meeting Notes",
    "From: team@company.com\nTo: all@company.com\nSubject: Project Update",
    "From: support@service.com\nTo: user@example.com\nSubject: Your Request",
    "From: noreply@system.com\nTo: user@example.com\nSubject: System Notification",
    "From: marketing@company.com\nTo: customers@company.com\nSubject: New Product Launch"
]

# Generate records data
records_data = []
record_ids = []
for i in range(100):  # Generate 100 records
    record_id = f"REC-{str(uuid.uuid4())[:8]}"
    record_ids.append(record_id)
    record = {
        "id": record_id
    }
    records_data.append(record)

# Write records to JSON file
with open('records_data.json', 'w') as f:
    json.dump(records_data, f, indent=2)

# Generate 8000 items
data = []
message_ids = []
start_date = datetime(2023, 1, 1)
for i in range(8000):
    # For the first message, use empty recipients list
    if i == 0:
        recipients = []
    else:
        # Randomly select 1-5 recipients
        num_recipients = random.randint(1, 5)
        recipients = random.sample(names, num_recipients)
    
    # Generate random date within 2023
    random_days = random.randint(0, 364)
    random_date = start_date + timedelta(days=random_days)
    date_str = random_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate bates numbers
    bates_prefix = f"ABC{random.randint(1000, 9999)}"
    beg_bates = f"{bates_prefix}-{random.randint(1, 999):03d}"
    end_bates = f"{bates_prefix}-{random.randint(1000, 1999):03d}"
    
    message_id = f"MSG-{str(uuid.uuid4())[:8]}"
    message_ids.append(message_id)
    
    item = {
        "author": random.choice(names),
        "beg_bates": beg_bates,
        "content": f"Sample message content {i} with some random text and information.",
        "datetime": date_str,
        "end_bates": end_bates,
        "headers": random.choice(sample_headers),
        "id": message_id,
        "index": i,
        "recipients": recipients
    }
    data.append(item)

# Write to JSON file
with open('recipients_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Generate relationship data
relationship_data = []
# Each record will have 1-20 random messages
for record_id in record_ids:
    num_messages = random.randint(1, 20)
    selected_messages = random.sample(message_ids, min(num_messages, len(message_ids)))
    for message_id in selected_messages:
        relationship = {
            "from": record_id,
            "to": message_id
        }
        relationship_data.append(relationship)

# Write relationship data to JSON file
with open('record_has_recipient_data.json', 'w') as f:
    json.dump(relationship_data, f, indent=2)

print("JSON files have been created successfully!")

try:
    os.system("rm -rf testdb")
except FileNotFoundError:
    pass

db = kuzu.Database("testdb")
conn = kuzu.Connection(db)

def print_result(result):
    while result.has_next():
        print(result.get_next())

# author : "STRING"
# beg_bates : "STRING"
# content : "STRING"
# datetime : "STRING"
# end_bates : "STRING"
# headers : "STRING"
# id : "STRING"
# index : "INT64"
# recipients : "STRING[]"

print_result(conn.execute("INSTALL json"))
print_result(conn.execute("LOAD json"))
print_result(conn.execute("CREATE NODE TABLE Record (id STRING PRIMARY KEY)"))
print_result(conn.execute("CREATE NODE TABLE Message (author STRING, beg_bates STRING, content STRING, datetime STRING, end_bates STRING, `headers` STRING, id STRING PRIMARY KEY, index INT64, recipients STRING[])"))
print_result(conn.execute("CREATE REL TABLE Record_HAS_Message (From Record TO Message)"))
print_result(conn.execute("COPY Record FROM 'records_data.json'"))
print_result(conn.execute("COPY Message FROM 'recipients_data.json'"))
print_result(conn.execute("COPY Record_HAS_Message FROM 'record_has_recipient_data.json'"))

# This will crash because one of the recipients is an empty list
print_result(conn.execute("""
match (n:Message)
where contains(list_to_string(n.recipients, ','), 'Alice')
return n.recipients
"""))

