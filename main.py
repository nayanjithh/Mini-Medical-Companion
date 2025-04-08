import requests, datetime, geocoder
import mic_and_speaker as ms
import gpt
# import oled, led
import monitoring as monitor
import threading
import time

monitoring_started = False

lat, lon = geocoder.ip("me").latlng or (10.824698, 76.645973)
WEATHER_URL = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

def toggle_lights():
    on = led.lights()
    msg = "Lights turned on" if on else "Lights turned off"
    # oled.emotion("Happiness")
    ms.speak(msg)

def weather_info():
    try:
        data = requests.get(WEATHER_URL).json()["current_weather"]
        desc = {
            0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 51: "Light drizzle", 61: "Light rain",
            63: "Moderate rain", 65: "Heavy rain", 71: "Light snow",
            73: "Moderate snow", 75: "Heavy snow"
        }.get(data["weathercode"], "Unknown")
        msg = f"{data['temperature']}°C, {data['windspeed']}km/h wind, {desc} weather."
        # oled.display(f"{desc}\n{data['temperature']}°C\n{data['windspeed']}km/h")
    except:
        msg = "Couldn't get weather info."
        # oled.emotion("Sadness")
    ms.speak(msg)

def tell_time():
    now = datetime.datetime.now()
    date, time = now.strftime("%d-%m-%Y"), now.strftime("%H:%M")
    # oled.display(f"{date}\n{time}")
    ms.speak(f"It's {date} and the time is {time}")

def operation(task):
    if task.startswith("__DATE_OR_TIME"): tell_time()
    elif task.startswith("__LIGHTS"): toggle_lights()
    elif task.startswith("__WEATHER"): weather_info()
    elif task.startswith("__HEALTH"): monitor.get_daily_summary()

def run_monitoring():
    monitor.check()
    threading.Timer(60, run_monitoring).start()

def start_conversation():
    while True:
        user = ms.listen()
        if not user: continue
        if user.lower() in ["thank you", "thanks", "no thanks", "stop"]:
            ms.speak("You're welcome"); break
        reply = gpt.ask_gpt(user)
        if reply.startswith("__"): operation(reply)
        else: ms.speak(reply)

if __name__ == "__main__":
    try:
        ms.speak("Hi, I am Mini. Nice to meet you.")
        if not monitoring_started:
            run_monitoring()
            monitoring_started = True

        while True:
            print("Say 'Hey Mini!' to activate...")
            wake = ms.listen()
            if not wake:
                continue

            if wake.lower() in ["hey mini", "hi mini", "mini"]:
                ms.speak("Yes, how can I help you?")
                start_conversation()
            elif wake.lower() in ["give me today's summary", "health report", "summary"]:
                monitor.get_daily_summary()
            elif wake.lower() in ["time please", "what's the time", "date"]:
                tell_time()
            time.sleep(1)

    except KeyboardInterrupt:
        print("👋 Exiting MINI gracefully.")
        ms.speak("Goodbye! Take care.")
