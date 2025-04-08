import pandas as pd
import mic_and_speaker as ms
import gpt

# Load dataset
df = pd.read_csv('datasets/safety_monitoring.csv')

def check():
    # Go through each record
    for i, row in df.iterrows():
        movement = str(row['Movement Activity']).strip().lower()
        fall_detected = str(row['Fall Detected (Yes/No)']).strip().lower() == 'yes'
        notified = str(row['Caregiver Notified (Yes/No)']).strip().lower() == 'no'
        location = str(row['Location'])

        # Handle missing values
        try:
            inactivity_duration = int(row['Post-Fall Inactivity Duration (Seconds)'])
        except:
            inactivity_duration = 0

        impact_level = str(row['Impact Force Level']).strip().lower()

        # 🔴 Fall Detected
        if fall_detected and notified:
            if impact_level == 'low':
                message = f"A fall was detected in the {location}. It appears to be minor. Please take a moment to rest and follow basic fall recovery tips."
            elif impact_level == 'medium':
                message = f"A fall of medium impact was detected in the {location}. Notifying caregiver immediately for assistance."
                df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes'
            elif impact_level == 'high':
                message = f"Severe fall detected in the {location}. Contacting emergency services right away."
                df.at[i, 'Caregiver Notified (Yes/No)'] = 'Yes'
            else:
                message = f"Fall detected in the {location}. Unable to determine severity. Please check on the user."

            print("🔴 MINI says:", message)
            ms.speak(message)
            df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes'

        # 🟡 Sedentary reminder based on inactivity duration
        elif inactivity_duration > 100 and movement in ['no movement', 'lying', 'sitting']:
            message = f"You've been inactive for over {inactivity_duration} seconds in the {location}. Please try moving or stretching a little."
            print("🟡 MINI says:", message)
            gpt.ask_gpt(f"I am inactive for over {inactivity_duration} seconds in the {location}.Tell me to moving or stretching a little.")
            df.at[i, 'Alert Triggered (Yes/No)'] = 'Yes'

        else:
            print(f"✅ Row {i}: No alert needed.")

    # Save the updated dataset
    df.to_csv('datasets/safety_monitoring.csv', index=False)
    print("✅ Safety monitoring dataset processed and saved.")