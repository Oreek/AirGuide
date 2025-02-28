import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import threading
import webbrowser
from main import air_navigation_mode

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash-001')

engine = pyttsx3.init()

recognizer = sr.Recognizer()

air_navigation_active = False

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def chat(prompt):
    try:
        response = model.generate_content("do not answer any prompt in long length/paragraphs. The prompt is:" + prompt)
        return response.text
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return "Sorry, I encountered an error."

def start_air_navigation_mode():
    global air_navigation_active
    air_navigation_active = True
    air_navigation_mode()
    air_navigation_active = False

def get_genres():
    genres = []
    while True:
        speak("Please tell me the next genre. If that's all, tell me now.")
        genre = listen()
        if genre and ("that is all" in genre.lower() or "that's all" in genre.lower() or "all done" in genre.lower() or "no more" in genre.lower()):
            break
        if genre:
            genres.append(genre.strip())
    return genres

def generate_linkedin_course_query(genres):
    prompt = f"""I want to learn skills in the following genres: {", ".join(genres)}.
    Give me a comma separated list of the best keywords to search for courses on LinkedIn Learning.
    Do not include any explanation or other text. Just the comma separated list.
    """
    try:
        response = model.generate_content(prompt)
        keywords = response.text.strip()
        return keywords
    except Exception as e:
        print(f"Error generating query: {e}")
        return None

def open_linkedin_learning_courses(query):
    if query:
        base_url = "https://www.linkedin.com/learning/search/"
        url = base_url + "?keywords=" + query.replace(", ", "+").replace(" ", "+")
        webbrowser.open_new_tab(url)
        print(f"Opening LinkedIn Learning courses: {url}")
        speak("I have opened the LinkedIn Learning courses for you.")
        return True
    else:
        print("No valid query to open LinkedIn Learning courses.")
        speak("I could not generate a valid query to open LinkedIn Learning courses.")
        return False

def main():
    speak("Welcome to this awesome LinkedIn courses recommender! Please tell me the genres you are interested in one by one.")

    genres = get_genres()

    if not genres:
        speak("No genres provided. Exiting.")
        return

    speak("Alright, generating a curated list of LinkedIn courses for you...")

    query = generate_linkedin_course_query(genres)

    if query:
        if open_linkedin_learning_courses(query):
            speak("Now, you can ask me anything.")
            while True:
                if not air_navigation_active:
                    user_input = listen()
                    if user_input:
                        if "exit" in user_input.lower() or "quit" in user_input.lower() or "bye" in user_input.lower():
                            speak("Goodbye!")
                            break
                        elif "air navigation" in user_input.lower():
                            speak("Starting air navigation mode.")
                            threading.Thread(target=start_air_navigation_mode).start()
                        else:
                            response = chat(user_input)
                            speak(response)
    else:
        speak("Could not generate a query. Exiting.")

if __name__ == "__main__":
    main()