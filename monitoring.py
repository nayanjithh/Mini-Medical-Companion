import pandas as pd
from datetime import datetime
import mic_and_speaker as ms
import gpt
import time

last_reset_day = None

# Thresholds
HR_MIN, HR_MAX = 60, 100
SYS_MIN, SYS_MAX = 90, 120
DIA_MIN, DIA_MAX = 60, 80
GLU_MIN, GLU_MAX = 70, 140
SPO2_MIN = 95

SUMMARY_LOG = 'datasets/daily_summary.csv'
HEALTH_LOG = 'datasets/health_monitoring.csv'
SAFETY_LOG = 'datasets/safety_monitoring.csv'
REMINDER_LOG = 'datasets/daily_reminder.csv'

def reset_daily_summary():
    # Create an empty DataFrame with the same columns
    columns = ['Device-ID/User-ID', 'Timestamp', 'Type', 'Issue Detected', 'Severity', 'Details']
    empty_df = pd.DataFrame(columns=columns)
    empty_df.to_csv(SUMMARY_LOG, index=False)
    print("🧹 Daily summary has been reset.")

def log_issue(user_id, timestamp, issue_type, issue, severity, details):
    df = pd.DataFrame([{
        'Device-ID/User-ID': user_id,
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M'),
        'Type': issue_type,
        'Issue Detected': issue,
        'Severity': severity,
        'Details': details
    }])
    try:
        existing = pd.read_csv(SUMMARY_LOG)
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        df.to_csv(SUMMARY_LOG, index=False)
        return
    df.to_csv(SUMMARY_LOG, index=False)

def get_daily_summary():
    ms.speak("Please tell me the numeric user ID you'd like the summary for.")
    user_id = ms.listen().strip()
    user_id = "D" + user_id.replace(" ", "").upper()
    
    if not user_id:
        ms.speak("Sorry, I didn't catch the user ID. Please try again.")
        return

    print(f"Got it. Preparing today's summary for user {user_id}.")
    ms.speak(f"Got it. Preparing today's summary for user {user_id}.")

    try:
        df = pd.read_csv(SUMMARY_LOG)
        today = datetime.now().strftime('%Y-%m-%d')

        # Filter by today's date and user_id
        today_df = df[
            (df['Timestamp'].str.startswith(today)) &
            (df['Device-ID/User-ID'].astype(str).str.lower() == str(user_id).lower())
        ]

        if today_df.empty:
            ms.speak(f"Great news. For {user_id}, no issues were detected today. Everything looks good.")
            return

        # Sort by timestamp
        today_df = today_df.sort_values(by='Timestamp')

        summary_text = f"Here is today's health and safety report for user {user_id}:\n"
        for _, row in today_df.iterrows():
            time_str = row['Timestamp'].split()[1]
            msg = f"At {time_str}, a {row['Type']} issue was detected: {row['Issue Detected']}. "
            msg += f"Severity level: {row['Severity']}. Details: {row['Details']}."
            print("📋 Summary:", msg)
            summary_text += msg + "\n"

        # Let GPT give advice based on the events
        response = gpt.ask_gpt(summary_text + " Based on this report, give some health or safety advice for the day.")
        print("MINI says:", response)
        ms.speak(response)
        
    except FileNotFoundError:
        ms.speak(f"Sorry, I couldn't find any summary file for today for user {user_id}.")


def check_reminder(now):
    reminder_df = pd.read_csv(REMINDER_LOG)
    for i, row in reminder_df.iterrows():
        try:
            row_time = datetime.strptime(row['Timestamp'], '%m/%d/%Y %H:%M')
        except Exception as e:
            print("⛔ Error parsing timestamp:", e)
            continue

        # Match time exactly to the minute
        if row_time.strftime('%m/%d/%Y %H:%M') == now.strftime('%m/%d/%Y %H:%M') and str(row['Reminder Sent (Yes/No)']).strip().lower() == 'no':
            reminder_type = row['Reminder Type']
            user_id = row['Device-ID/User-ID']
            scheduled_time = row['Scheduled Time']
            msg = f"{user_id} has {reminder_type} scheduled at {scheduled_time} today"
            print("🔔 Reminder:", msg)
            response = gpt.ask_gpt(f"Notify {user_id} about the {reminder_type} scheduled at {scheduled_time} today")
            print("MINI says:", response)
            ms.speak(response)
            reminder_df.at[i, 'Reminder Sent (Yes/No)'] = 'Yes'

    reminder_df.to_csv(REMINDER_LOG, index=False)

def check_heart(now):
    health_df = pd.read_csv(HEALTH_LOG)

    for i, row in health_df.iterrows():
        try:
            row_time = datetime.strptime(row['Timestamp'], '%m/%d/%Y %H:%M')
        except Exception as e:
            print("⛔ Error parsing timestamp:", e)
            continue

        if row_time.strftime('%m/%d/%Y %H:%M') == now.strftime('%m/%d/%Y %H:%M'):
            # Process each health metric
            try:
                hr = int(row['Heart Rate'])
                health_df.at[i, 'Heart Rate Below/Above Threshold (Yes/No)'] = 'Yes' if hr < HR_MIN or hr > HR_MAX else 'No'
            except:
                health_df.at[i, 'Heart Rate Below/Above Threshold (Yes/No)'] = 'Yes'

            try:
                sys, dia = map(int, row['Blood Pressure'].split('/')[0:2])
                bp_flag = 'Yes' if sys < SYS_MIN or sys > SYS_MAX or dia < DIA_MIN or dia > DIA_MAX else 'No'
            except:
                bp_flag = 'Yes'
            health_df.at[i, 'Blood Pressure Below/Above Threshold (Yes/No)'] = bp_flag

            try:
                glucose = int(row['Glucose Levels'])
                health_df.at[i, 'Glucose Levels Below/Above Threshold (Yes/No)'] = 'Yes' if glucose < GLU_MIN or glucose > GLU_MAX else 'No'
            except:
                health_df.at[i, 'Glucose Levels Below/Above Threshold (Yes/No)'] = 'Yes'

            try:
                spo2 = int(row['Oxygen Saturation (SpO₂%)'])
                health_df.at[i, 'SpO₂ Below Threshold (Yes/No)'] = 'Yes' if spo2 < SPO2_MIN else 'No'
            except:
                health_df.at[i, 'SpO₂ Below Threshold (Yes/No)'] = 'Yes'

            alert = any(health_df.at[i, col] == 'Yes' for col in [
                'Heart Rate Below/Above Threshold (Yes/No)',
                'Blood Pressure Below/Above Threshold (Yes/No)',
                'Glucose Levels Below/Above Threshold (Yes/No)',
                'SpO₂ Below Threshold (Yes/No)'
            ])
            health_df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes' if alert else 'No'
            health_df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes' if alert else 'No'

    # 🔥 This runs **after scanning** all rows:
    today_df = health_df[health_df['Timestamp'].str.contains(now.strftime('%m/%d/%Y'))]
    if not today_df.empty:
        latest = today_df.iloc[-1]
        if str(latest['Alert Triggered (Yes/No)']).strip().lower() == 'yes':
            user_id = row['Device-ID/User-ID']
            print(f"Warning.In {user_id} abnormal health vitals detected.")
            ms.speak(f"Warning.In {user_id} abnormal health vitals detected.")
            if latest['Heart Rate Below/Above Threshold (Yes/No)'] == 'Yes':
                response = gpt.ask_gpt(f"What to do if Heart rate is at {latest['Heart Rate']} BPM")
                print("MINI says:", response)
                ms.speak(response)
                log_issue(user_id, now, "Health", "Heart Rate", "Moderate", f"HR = {latest['Heart Rate']} BPM")

            if latest['Blood Pressure Below/Above Threshold (Yes/No)'] == 'Yes':
                response = gpt.ask_gpt(f"What to do if Blood Pressure is at {latest['Blood Pressure']}")
                print("MINI says:", response)
                ms.speak(response)
                log_issue(user_id, now, "Health", "Blood Pressure", "Moderate", f"BP = {latest['Blood Pressure']}")

            if latest['Glucose Levels Below/Above Threshold (Yes/No)'] == 'Yes':
                response = gpt.ask_gpt(f"What to do if Glucose Level is at {latest['Glucose Levels']}")
                print("MINI says:", response)
                ms.speak(response)
                log_issue(user_id, now, "Health", "Glucose Level", "Moderate", f"Glucose = {latest['Glucose Levels']}")

            if latest['SpO₂ Below Threshold (Yes/No)'] == 'Yes':
                response = gpt.ask_gpt(f"What to do if SpO₂ is at {latest['Oxygen Saturation (SpO₂%)']}%")
                print("MINI says:", response)
                ms.speak(response)
                log_issue(user_id, now, "Health", "SpO₂", "Moderate", f"SpO₂ = {latest['Oxygen Saturation (SpO₂%)']}%")
        else:
            print("✅ No abnormal vitals now.")

    health_df.to_csv(HEALTH_LOG, index=False)

def check_safety(now):
    safety_df = pd.read_csv(SAFETY_LOG)

    for i, row in safety_df.iterrows():
        try:
            row_time = datetime.strptime(row['Timestamp'], '%m/%d/%Y %H:%M')
        except Exception as e:
            print(f"⛔ Row {i} timestamp error:", e)
            continue

        # Match time exactly to the minute
        if row_time.strftime('%m/%d/%Y %H:%M') == now.strftime('%m/%d/%Y %H:%M'):
            movement = str(row['Movement Activity']).strip().lower()
            fall_detected = str(row['Fall Detected (Yes/No)']).strip().lower() == 'yes'
            notified = str(row['Caregiver Notified (Yes/No)']).strip().lower() == 'no'
            location = row.get('Location', 'unknown')
            impact_level = str(row['Impact Force Level']).strip().lower()

            try:
                inactivity_duration = int(row['Post-Fall Inactivity Duration (Seconds)'])
                user_id = row['Device-ID/User-ID']
            except:
                inactivity_duration = 0

            if fall_detected and notified:
                if impact_level == 'low':
                    msg = f"{user_id} has fallen in the {location}. It appears to be minor."
                elif impact_level == 'medium':
                    msg = f"{user_id} has fallen in the {location} with a medium-impact. Notifying caregiver."
                    safety_df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes'
                elif impact_level == 'high':
                    msg = f"{user_id} has fallen in the {location} with a high-impact. Contacting emergency services."
                    safety_df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes'
                else:
                    msg = f"{user_id} has fallen in the {location}. Severity unknown."

                print("🔴 MINI says:", msg)
                ms.speak(msg)
                log_issue(user_id, now, "Safety", "Fall Detected", impact_level.capitalize(), f"Fall in {location} with {impact_level} impact")
                safety_df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes'

            elif inactivity_duration > 100 and movement in ['no movement', 'lying', 'sitting']:
                msg = f"You've been inactive for {inactivity_duration} seconds in {location}. Please stretch."
                print("🟡 MINI says:", msg)
                response = gpt.ask_gpt(f"I've been inactive for {inactivity_duration} seconds in the {location}. Notify me and tell me to stretch.")
                print("MINI says:", response)
                ms.speak(response)
                log_issue(now, "Safety", "Inactivity", "Low", f"{inactivity_duration}s inactivity in {location}")
                safety_df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes'
            else:
                print(f"✅ Row {i}: No alert.")

    # ✅ Save after loop completes
    safety_df.to_csv(SAFETY_LOG, index=False)

def check():
    global last_reset_day
    now = datetime.now().replace(second=0, microsecond=0)
    print(f"🔁 Checking at {now.strftime('%H:%M')} on {now.strftime('%m/%d/%Y')}")
    
    check_heart(now)
    print("Heart checked")
    #time.sleep(10)
    check_safety(now)
    print("Safty checked")
    #time.sleep(10)
    check_reminder(now)
    print("Reminders checked")
    #time.sleep(10)

    if now.hour == 23 and now.minute == 59:
        if last_reset_day != now.date():
            reset_daily_summary()
            last_reset_day = now.date()

if __name__ == "__main__":
    while True:
        check()
        time.sleep(5)  # Checks every 1 min
