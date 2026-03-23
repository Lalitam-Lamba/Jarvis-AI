import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import random
import wikipedia
from bs4 import BeautifulSoup
import time

load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init('sapi5')   # VERY IMPORTANT (for Windows)

voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
else:
    print("Warning: No voices found. Check TTS settings.")

engine.setProperty('rate', 170)
engine.setProperty('volume', 1.0)

newsapi = os.getenv("NEWS_API_KEY")
weather_api = os.getenv("WEATHER_API_KEY")
email_user = os.getenv("EMAIL_USER")
email_password = os.getenv("EMAIL_PASSWORD")
stock_api = os.getenv("STOCK_API_KEY", "")

# Command logging
command_log = []
reminders = []



def speak(text):
    print("Speaking:", text)
    try:
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.5)  # Small delay to ensure audio completes
    except Exception as e:
        print(f"Speak error: {e}")
        time.sleep(1)

def log_command(command):
    """Log commands for history"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command_log.append(f"{timestamp}: {command}")
    with open("command_log.txt", "a") as f:
        f.write(f"{timestamp}: {command}\n")

def get_time():
    """Get current time"""
    time_str = datetime.now().strftime("%I:%M %p")
    speak(f"The time is {time_str}")

def get_date():
    """Get current date"""
    date_str = datetime.now().strftime("%B %d, %Y")
    speak(f"Today is {date_str}")

def get_weather(city="Delhi"):
    """Get weather information"""
    try:
        if weather_api:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                condition = data['weather'][0]['description']
                speak(f"In {city}, it's {temp} degrees and {condition}")
            else:
                speak("Could not fetch weather data")
        else:
            speak("Weather API key not configured")
    except Exception as e:
        print(f"Weather error: {e}")
        speak("Sorry, I couldn't get the weather")

def calculator(expression):
    """Simple calculator"""
    try:
        result = eval(expression)
        speak(f"The answer is {result}")
        return result
    except Exception as e:
        speak("Invalid calculation")
        return None

def send_email(recipient, subject, body):
    """Send email"""
    try:
        if not email_user or not email_password:
            speak("Email credentials not configured")
            return
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_password)
        
        message = MIMEMultipart()
        message["From"] = email_user
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        server.send_message(message)
        server.quit()
        speak(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Email error: {e}")
        speak("Failed to send email")

def get_stocks(symbol):
    """Get stock price"""
    try:
        if stock_api:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={stock_api}"
            response = requests.get(url, timeout=5)
            data = response.json()
            price = data.get('Global Quote', {}).get('05. price', 'Not found')
            speak(f"{symbol} is trading at {price}")
        else:
            speak("Stock API key not configured")
    except Exception as e:
        print(f"Stock error: {e}")
        speak("Could not fetch stock price")

def search_wikipedia(query):
    """Search Wikipedia"""
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        return result
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific")
    except wikipedia.exceptions.PageError:
        speak("Page not found on Wikipedia")
    except Exception as e:
        print(f"Wikipedia error: {e}")
        speak("Could not search Wikipedia")

def tell_joke():
    """Tell a joke"""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
        if response.status_code == 200:
            joke_data = response.json()
            joke = f"{joke_data['setup']} {joke_data['punchline']}"
            speak(joke)
        else:
            speak("Could not fetch a joke")
    except Exception as e:
        print(f"Joke error: {e}")
        speak("Could not get a joke")

def processCommand(c):
    log_command(c)
    
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        try:
            song = c.lower().split(" ")[1]
            link = musiclibrary.music.get(song)
            if link:
                webbrowser.open(link)
            else:
                speak(f"Song {song} not found in library")
        except (IndexError, KeyError):
            speak("Please specify a song name")
    elif c.lower().startswith("news"):
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}"
            r = requests.get(url, timeout=5)

            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                if articles:
                    for article in articles[:3]:  # Get top 3 articles
                        speak(article['title'])
                else:
                    speak("No news articles found")
            else:
                speak("Failed to fetch news")
        except Exception as e:
            print(f"News error: {e}")
            speak("Could not fetch news")
    
    elif "what time" in c.lower():
        get_time()
    elif "what is the time" in c.lower():
        get_time()
    elif "current time" in c.lower():
        get_time()
    
    elif "what date" in c.lower() or "what is the date" in c.lower():
        get_date()
    elif "today" in c.lower() and "date" in c.lower():
        get_date()
    
    elif "weather" in c.lower():
        city = "Delhi"
        if "in" in c.lower():
            try:
                city = c.lower().split("in")[-1].strip()
            except:
                pass
        get_weather(city)
    
    elif "calculate" in c.lower():
        try:
            expr = c.lower().replace("calculate", "").strip()
            calculator(expr)
        except:
            speak("Invalid calculation")
    
    elif "joke" in c.lower():
        tell_joke()
    
    elif "wikipedia" in c.lower() or "search" in c.lower():
        query = c.lower().replace("wikipedia", "").replace("search", "").strip()
        search_wikipedia(query)
    
    elif "stock" in c.lower():
        try:
            symbol = c.upper().split("STOCK")[-1].strip()
            get_stocks(symbol)
        except:
            speak("Please specify a stock symbol")
    
    elif "send email" in c.lower():
        speak("To email address?")
        # This would need voice input for recipient
        speak("Feature requires configuration")
    
    elif "reminder" in c.lower() or "remind me" in c.lower():
        try:
            reminder_text = c.lower().replace("reminder", "").replace("remind me", "").strip()
            reminders.append(reminder_text)
            speak(f"Reminder set: {reminder_text}")
        except:
            speak("Could not set reminder")
    
    elif "show reminders" in c.lower() or "list reminders" in c.lower():
        if reminders:
            speak(f"You have {len(reminders)} reminders")
            for reminder in reminders:
                speak(reminder)
        else:
            speak("No reminders set")
    
    elif "command history" in c.lower() or "show history" in c.lower():
        if command_log:
            speak(f"You have {len(command_log)} commands in history")
        else:
            speak("No command history")

if (__name__ == "__main__"):
        speak("Initializing Jarvis...")
        time.sleep(1)
        
        while True:
            recognizer = sr.Recognizer()
            print("Recognizing...")

            try:
                with sr.Microphone() as source:
                    print("Listening for 'Jarvis'...")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")
                log_command(f"Heard: {word}")
                
                if(word.lower() == "jarvis"):
                    speak("Yaa")
                    log_command("Responded: Yaa")
                    time.sleep(0.5)
                    
                    # Listen for commands continuously until user says stop
                    command_mode = True
                    while command_mode:
                        try:
                            recognizer = sr.Recognizer()
                            with sr.Microphone() as source:
                                print("Jarvis Active... Listening for command...")
                                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                                command = recognizer.recognize_google(audio)
                                print(f"Command: {command}")
                                
                                # Check for stop commands
                                if "stop" in command.lower() or "exit" in command.lower() or "bye" in command.lower():
                                    speak("Goodbye!")
                                    log_command("Session ended")
                                    command_mode = False
                                else:
                                    processCommand(command)
                        
                        except sr.UnknownValueError:
                            print("Could not understand audio")
                            speak("Sorry, I didn't catch that")
                        except sr.Timeout:
                            print("Timeout: No speech detected, still listening...")
                        except sr.RequestError as e:
                            print(f"API Error: {e}")
                            speak("There was an issue with the speech recognition service")
                        except Exception as e:
                            print(f"Error: {e}")

            except sr.UnknownValueError:
                print("Could not understand audio")
                speak("Sorry, I didn't catch that")
            except sr.RequestError as e:
                print(f"API Error: {e}")
                speak("There was an issue with the speech recognition service")
            except sr.Timeout:
                print("Timeout: No speech detected")
            except Exception as e:
                print(f"Error: {e}")