import datetime
import AppOpener
import openai
import pyjokes
import pyttsx3
import pywhatkit
import spacy
import speech_recognition as sr
import wikipedia

# Initialize OpenAI API
# Remember to use your own openAi api key !!

openai.api_key = ''

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
jervis = pyttsx3.init()
voices = jervis.getProperty('voices')
jervis.setProperty('voice', voices[1].id)


def talk(text):
    """Speaks the provided text."""
    jervis.say(text)
    jervis.runAndWait()


def take_command():
    """Listens for a command and returns it as text."""
    command = ""  # Initialize command to an empty string
    try:
        with sr.Microphone() as source:
            print("Listening...")
            if not hasattr(take_command, "one_time"):
                talk("Hi sir, how can I assist you?")
                take_command.one_time = True

            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'jervis' in command:
                command = command.replace('jervis', '')

    except sr.UnknownValueError:
        talk("Sorry, I did not get that. Please repeat.")
    except sr.RequestError:
        talk("Sorry, my speech service is down.")
    except Exception as e:
        print(f"Error: {e}")

    return command


# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def process_command(command):
    """Processes the command using NLP to extract entities and intents."""
    doc = nlp(command)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    intents = [token.lemma_ for token in doc if token.dep_ == 'ROOT']
    return entities, intents


def get_gpt_response(prompt):
    """Gets a response from the GPT model for a given prompt."""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


def run_jervis():
    """Main function to run the Jervis assistant."""
    while True:
        command = take_command()

        if not command:
            continue

        entities, intents = process_command(command)
        print(f"Entities: {entities}")
        print(f"Intents: {intents}")

        if 'bye' in command:
            talk("Goodbye, sir.")
            break
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            print(time)
            talk('Current time is ' + time)
        elif 'play' in command:
            vedio = command.replace('play', '').strip()
            talk("Playing " + vedio)
            pywhatkit.playonyt(vedio)
        elif 'tell me about' in command:
            look_for = command.replace('tell me about', '').strip()
            info = wikipedia.summary(look_for, sentences=1)
            print(info)
            talk(info)
        elif 'joke' in command:
            joke = pyjokes.get_joke()
            talk(joke)
            print(joke)
        elif 'date' in command:
            talk('Sorry sir, I am in another relationship.')
        elif 'open app' in command or 'open a web page' in command:
            talk("Which app, sir?")
            app_command = take_command()
            app = f"{app_command.lower()}"
            # if 'chaapp_tbot' in app_command:
            #     talk("Opening ChatGPT.")
            #     webbrowser.open('https://www.chatgpt.com')
            if app in app_command:
                talk(f"Opening {app}")
                AppOpener.open(app, match_closest=True)
            # elif 'gmail' in app_command:
            #     talk("Opening Gmail.")
            #     AppOpener.open("Gmail")
            # elif "vs code" in app_command:
            #     talk("Opening Visual Studio Code.")
            #     AppOpener.open("Visual Studio Code")
            # elif 'facebook' in app_command:
            #     talk("Opening Facebook.")
            #     AppOpener.open("Facebook")
            # elif 'youtube' in app_command:
            #     talk("Opening YouTube.")
            #     AppOpener.open("YouTube")
            # elif 'instagram' in app_command:
            #     talk("Opening Instagram.")
            #     AppOpener.open("Instagram")
            # elif 'google site' in app_command:
            #     talk("Opening Google Sites.")
            #     AppOpener.open("google site")
            # elif "google chrome" in app_command:
            #     talk("Opening Google Chrome.")
            #     AppOpener.open("google chrome")
            # elif "microsoft edge" in app_command:
            #     talk("Opening Microsoft Edge.")
            #     AppOpener.open("microsoft edge")
            # elif "whatsapp" in app_command:
            #     talk("Opening WhatsApp.")
            #     AppOpener.open("whatsapp")
            # elif "messenger" in app_command:
            #     talk("Opening Messenger.")
            #     AppOpener.open("Messenger")

            talk("Done.")
            print("Done.")
        else:
            try:
                # Try Wikipedia first
                info = wikipedia.summary(command, sentences=2)
                talk(info)
                print(info)
            except wikipedia.DisambiguationError as e:
                talk("Your query is ambiguous. Can you be more specific?")
                print("DisambiguationError: ", e)
            except wikipedia.PageError:
                # If Wikipedia fails, fall back to GPT
                gpt_response = get_gpt_response(command)
                talk(gpt_response)
                print(gpt_response)
            except Exception as e:
                talk("I encountered an error while searching for information.")
                print("Error: ", e)


run_jervis()
