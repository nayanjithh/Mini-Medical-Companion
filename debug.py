def check_reminder(now):
    reminder_df = pd.read_csv(REMINDER_LOG)
    for i, row in reminder_df.iterrows():
        try:
            row_time = pd.to_datetime(f"{row['Timestamp'].split()[0]} {row['Scheduled Time'][:5]}")
            row_time = row_time.replace(second=0, microsecond=0)
        except:
            continue
        if row_time.strftime('%m/%d/%Y %H:%M') == now.strftime('%m/%d/%Y %H:%M') and row['Reminder Sent (Yes/No)'].strip().lower() == 'no':
            reminder_type = row['Reminder Type']
            msg = f"It's time for your {reminder_type}."
            print("🔔 Reminder:", msg)
            gpt.ask_gpt(f"Its time for my {reminder_type} notify me")
            reminder_df.at[i, 'Reminder Sent (Yes/No)'] = 'Yes'

    reminder_df.to_csv(REMINDER_LOG, index=False)