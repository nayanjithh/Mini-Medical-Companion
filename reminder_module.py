import pandas as pd
from datetime import datetime
import gpt
import time

def check_reminder():
    df = pd.read_csv('datasets/daily_reminder.csv')
    now = datetime.now().replace(second=0, microsecond=0)
    today = now.strftime('%m/%d/%Y')
    current_time = now.strftime('%H:%M')

    print(f"Checking reminders at {current_time} on {today}")

    for i, row in df.iterrows():
        try:
            scheduled_dt = pd.to_datetime(f"{row['Timestamp'].split()[0]} {row['Scheduled Time'][:5]}")
        except:
            continue

        if scheduled_dt == now and row['Reminder Sent (Yes/No)'].strip().lower() == 'no':
            reminder_type = row['Reminder Type']
            msg = f"It's time for your {reminder_type}."
            print(msg)
            gpt.ask_gpt(f"Tell me that its time for my {reminder_type}")

            df.at[i, 'Reminder Sent (Yes/No)'] = 'Yes'

            # Ack
        else:
            print(f"Skipping row: {row['Reminder Type']} — Not time yet or already sent.")

    df.to_csv("datasets/daily_reminder.csv", index=False)

while True:
    check_reminders()
    time.sleep(60)