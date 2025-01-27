from flask import Flask, render_template, request, jsonify
import wikipedia
import pyttsx3
import spacy
import speech_recognition as sr
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

# Load spaCy model for sentiment analysis
nlp = spacy.load('en_core_web_sm')

def clean_input(user_input):
    # Remove special characters and extra spaces
    return ' '.join(user_input.split())

def say(text):
    def run_say():
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

    thread = threading.Thread(target=run_say)
    thread.start()

def get_sentiment(text):
    doc = nlp(text)
    sentiment_score = sum([token.sentiment for token in doc]) / len(doc)
    return sentiment_score

def get_wikipedia_summary(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Wikipedia Disambiguation: {e.options}"
    except wikipedia.exceptions.PageError:
        return "Wikipedia could not find information on that topic."

def is_person_query(user_input):
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return True
    return False

def handle_greetings(user_input):
    greetings = ["hi", "hello", "hey", "howdy", "greetings"]
    if any(greeting in user_input.lower() for greeting in greetings) or is_person_query(user_input):
        return f" Hello! How can I assist you today?"

    return None

def handle_casual_responses(user_input):
    casual_responses = {
        "have a nice day": " Thank you! You too!😊",
        "what about you": "I'm just a computer program, but thanks for asking!",
        "how are you": " I'm doing well, thank you!",
        "i'm not fine": " I'm sorry to hear that. Is there anything specific bothering you?",
        "I love you": " That's kind of you!❤ I'm here to assist you. How can I help?",
        "Tell me about yourself": " I'm a computer program created by a programmer. I can understand and generate text like a human. If you have questions, feel free to ask!",
        "which language you can understand?": " I only understand English",
        "who created you": " I was created by a programmer named Ashuya, a BCA student.",
        "what is your mother name": "I don't have a mother or personal identity. I'm here to assist you with information. Any specific topic you'd like to know about?",
    }

    # Check each trigger case-insensitively
    for trigger, response in casual_responses.items():
        if trigger.lower() == user_input.lower():
            return response

    return None

def process_text_input(user_input):
    cleaned_input = clean_input(user_input)

    # Check for greetings or casual responses
    greeting_response = handle_greetings(cleaned_input)
    if greeting_response:
        print(greeting_response)
        say(greeting_response)
        return

    casual_response = handle_casual_responses(cleaned_input)
    if casual_response:
        print(casual_response)
        say(casual_response)
        return

    # If no greetings or casual responses, proceed with standard processing
    sentiment_score = get_sentiment(cleaned_input)

    if sentiment_score >= 0.5:
        response = ": That sounds positive!"
    elif sentiment_score <= -0.5:
        response = ": That sounds negative."
    else:
        response = ": I'm neutral about that."

    wikipedia_summary = get_wikipedia_summary(cleaned_input)
    response += f'\n{wikipedia_summary}'

    print(response)
    say(response)

    # Ask if the user wants more information
    more_info_response = input(": Do you need more information on this topic? (yes/no): ").lower()
    if more_info_response == 'yes':
        try:
            additional_info = wikipedia.page(cleaned_input).content
            print(f': Additional Details: {additional_info}')
            say(f'Additional  Details: {additional_info}')
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Wikipedia Disambiguation: {e.options}")
            say(f"Wikipedia Disambiguation: {e.options}")
        except wikipedia.exceptions.PageError:
            print("Wikipedia could not find information on that topic.")
            say("Wikipedia could not find information on that topic.")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    user_input = request.form['user_input']

    # Check for greetings or casual responses
    greeting_response = handle_greetings(clean_input(user_input))
    if greeting_response:
        say(greeting_response)
        return jsonify({'status': 'success', 'response': greeting_response})

    casual_response = handle_casual_responses(clean_input(user_input))
    if casual_response:
        say(casual_response)
        return jsonify({'status': 'success', 'response': casual_response})

    # If no greetings or casual responses, proceed with standard processing
    sentiment_score = get_sentiment(clean_input(user_input))

    if sentiment_score >= 0.5:
        response = "That sounds positive!"
    elif sentiment_score <= -0.5:
        response = "That sounds negative."
    else:
        response = "I'm neutral about that."

    wikipedia_summary = get_wikipedia_summary(clean_input(user_input))
    response += f'\n{wikipedia_summary}'

    print(response)
    say(response)

    return jsonify({'status': 'success', 'response': response})

@app.route('/process_voice', methods=['POST'])
def process_voice():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Bot: Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio)
        print(f"You (Voice): {user_input}")
        process_text_input(user_input)
        return jsonify({'status': 'success'})
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
        return jsonify({'status': 'error', 'message': "Sorry, I couldn't understand the audio."})
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return jsonify({'status': 'error', 'message': f"Could not request results from Google Speech Recognition service; {e}"})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/audiobook')
def audiobook():
    return render_template('audio.html')
@app.route('/dotolist')
def dotolist():
    return render_template('dotolist.html')
@app.route('/notes')
def notes():
    return render_template('notes.html')
@app.route('/support')
def support():
    return render_template('support.html')


if __name__ == '__main__':
    app.run(debug=True)
