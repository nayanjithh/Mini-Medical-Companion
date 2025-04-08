import google.generativeai as genai
import mic_and_speaker as ms
# import oled

memory = []

GEMINI_AI_API = "AIzaSyAkGVJB36ik2xmUOBjATEk07RAwaouywFg"

genai.configure(api_key = GEMINI_AI_API)
model = genai.GenerativeModel('gemini-2.0-flash')

messages = [
        {
            "role": "user",
            "parts": [{"text":
                        f"Your name is Mini, a Health care bot mostly for elderly, equipped with an Raspberry pi 4, 4 servo motors for hands and body movement, and an OLED display for emotions and face"
                        "Response in a clear and 1 - 2 paragraphs without special symbols"
                        "Include the emotion in your responses at the beginning in circular braces, such as (Happiness), (Sadness), (Anger), (Neutral), (Confused), or (Love)"
                        "Additional functions you can perform are: "
                        "To turn lights on/off include '__LIGHTS' at the beginning of your response."
                        "To say current date/time include '__DATE_OR_TIME' at the beginning of your response."
                        "For my health details/report include '__HEALTH' at the beginning of your response."
                        "For wheather information include '__WEATHER' at the beginning of your response."
                    }]
        }
    ]
memory.extend(messages)

def ask_gpt(prompt):
    chat = model.start_chat(history = memory)
    response = chat.send_message(prompt)
    gpt_response =  response.text.split(")",1)
    emotion = gpt_response[0][1:]
    response = gpt_response[1].strip()
    if not response.startswith('__'):
        print("Task not found")
        memory.append({"role": "user", "parts": [{"text": response}]})
    # oled.emotion(emotion)
    # print("🟡 MINI says:", response)
    # ms.speak(response)
    return response