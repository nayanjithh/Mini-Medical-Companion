import pandas as pd
import mic_and_speaker as ms
import gpt

# Load dataset
df = pd.read_csv('datasets/health_monitoring.csv')

# Thresholds
HR_MIN, HR_MAX = 60, 100
SYS_MIN, SYS_MAX = 90, 120
DIA_MIN, DIA_MAX = 60, 80
GLU_MIN, GLU_MAX = 70, 140
SPO2_MIN = 95

def check():
    for i, row in df.iterrows():
        # Heart Rate
        hr = int(row['Heart Rate'])
        df.at[i, 'Heart Rate Below/Above Threshold (Yes/No)'] = 'Yes' if hr < HR_MIN or hr > HR_MAX else 'No'

        # Blood Pressure
        try:
            bp_parts = row['Blood Pressure'].split('/')
            sys = int(bp_parts[0])
            dia = int(bp_parts[1].split()[0])
            bp_flag = 'Yes' if sys < SYS_MIN or sys > SYS_MAX or dia < DIA_MIN or dia > DIA_MAX else 'No'
        except:
            bp_flag = 'Yes'
        df.at[i, 'Blood Pressure Below/Above Threshold (Yes/No)'] = bp_flag

        # Glucose
        glucose = int(row['Glucose Levels'])
        df.at[i, 'Glucose Levels Below/Above Threshold (Yes/No)'] = 'Yes' if glucose < GLU_MIN or glucose > GLU_MAX else 'No'

        # SpO2
        spo2 = int(row['Oxygen Saturation (SpO₂%)'])
        df.at[i, 'SpO₂ Below Threshold (Yes/No)'] = 'Yes' if spo2 < SPO2_MIN else 'No'

        # Alert and caregiver notify flags
        alert = (
            df.at[i, 'Heart Rate Below/Above Threshold (Yes/No)'] == 'Yes' or
            df.at[i, 'Blood Pressure Below/Above Threshold (Yes/No)'] == 'Yes' or
            df.at[i, 'Glucose Levels Below/Above Threshold (Yes/No)'] == 'Yes' or
            df.at[i, 'SpO₂ Below Threshold (Yes/No)'] == 'Yes'
        )
        df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes' if alert else 'No'
        df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes' if alert else 'No'

    # Save the updated dataset
    df.to_csv('datasets/health_monitoring.csv', index=False)

    # Step 2: Alert based on the latest row
    latest = df.iloc[-1]

    if latest['Alert Triggered (Yes/No)'].strip().lower() == 'yes':
        message = "Warning. Abnormal health vitals detected. Procced as i say"
        print("🔴 MINI says:", message)
        ms.speak(message)

        # Print out abnormal readings
        if latest['Heart Rate Below/Above Threshold (Yes/No)'] == 'Yes':
            print(f"  ⚠️ Heart Rate: {latest['Heart Rate']} BPM")
            gpt.ask_gpt(f"What to do if Heart rate is at {latest['Heart Rate']} BPM")

        if latest['Blood Pressure Below/Above Threshold (Yes/No)'] == 'Yes':
            print(f"  ⚠️ Blood Pressure: {latest['Blood Pressure']}")
            gpt.ask_gpt(f"What to do if Blood Pressure is at {latest['Blood Pressure']}")

        if latest['Glucose Levels Below/Above Threshold (Yes/No)'] == 'Yes':
            print(f"  ⚠️ Glucose Level: {latest['Glucose Levels']} mg/dL")
            gpt.ask_gpt(f"What to do if Glucose Level at {latest['Glucose Levels']} mg/dL")

        if latest['SpO₂ Below Threshold (Yes/No)'] == 'Yes':
            print(f"  ⚠️ SpO₂: {latest['Oxygen Saturation (SpO₂%)']}%")
            gpt.ask_gpt(f"What to do if SpO₂ at {latest['Oxygen Saturation (SpO₂%)']}%")
    else:
        print("✅ No abnormal vitals. MINI is happy.")

    print("Vitals dataset updated successfully!")
