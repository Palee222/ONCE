import numpy as np
import os
import re
import unicodedata

#!/usr/bin/env python3
'''
Used recognition thingy for speech:

https://pypi.org/project/SpeechRe0cognition/
https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
python3 -m venv .venv
source .venv/bin/activate
python -m pip install SpeechRecognition numpy
python speech-text.py
python -m pip install "SpeechRecognition[audio]" numpy
brew install portaudio
python -m pip install --no-cache-dir PyAudio
python -c "import pyaudio; print('PyAudio installed')"
python speech-text.py

This is the text to speech modult
https://pypi.org/project/pyttsx3/
pip install pyttsx3

possible commands:
- inicia el proceso
- sacar la comida
- poner comida
'''

#this is the speech recognition modul
#find the information on the above link
import speech_recognition as sr

#I just imported this for audio feedback for our users
import pyttsx3
engine = pyttsx3.init()

minutes_on_micro = list(range(1, 36))

SPANISH_MINUTES = {
    "uno": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiuno": 21, "veintidos": 22, "veintitres": 23,
    "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "treinta y uno": 31, "treinta y dos": 32,
    "treinta y tres": 33, "treinta y cuatro": 34, "treinta y cinco": 35,
}

def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"[^\w\s]", "", normalized).strip()


def parse_command(transcript: str):
    text = normalize_text(transcript)
    time_match = re.search(r"\bajusta el tiempo a (.+?) minutos?\b", text)

    if time_match:
        spoken_minutes = time_match.group(1).strip()
        if spoken_minutes.isdigit():
            minutes = int(spoken_minutes)
        else:
            minutes = SPANISH_MINUTES.get(spoken_minutes)

        if minutes in minutes_on_micro:
            return {"action": "set_time", "minutes": minutes}
        return None

    commands = {
        "inicia el proceso": "start",
        "sacar la comida": "remove_food",
        "poner comida": "add_food",
    }
    for phrase, action in commands.items():
        if phrase in text:
            return {"action": action}
    return None


def speech_recognition(): 
    
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        transcript = recognizer.recognize_google(audio, language="es-ES")
        print(f"Escuché: {transcript}")
        return parse_command(transcript)
    except sr.WaitTimeoutError:
        print("No se detectó voz a tiempo.")
    except sr.UnknownValueError:
        print("No pude entender el audio.")
    except sr.RequestError as error:
        print(f"Error del servicio de reconocimiento: {error}")
    return 0

def to_arm():
    #take that text from the speech_recognition and send it to the arm to make it move
    #take the command and send it to the arm to make it move
    taken_command = speech_recognition()
    if taken_command is None:
        print("No entendí el comando. Inténtalo de nuevo.")
    
    '''
    Here I dont know how to send the command to the arm to make it move. So I let you you connect it to the arm and make it move
    '''
    
    return 0

def feedback(command):
    #give visual and audio feedback on starting the process, setting the minutes to x and putting/taking food
    '''
    The visual feedback would be just a UI with a red and green lamp. The red turns on when the arm is doing nothing and green turns on when the arm understood the command and is in the process
    of doing it. Also, there would be a text feedback like "Doing the process...".
    
    For audio feedback it would be almost the same, just feedback is being said. For example, "Setting time for x minutes" or "Starting process".
    '''
    #audio feedback for the user
    if command is None:
        engine.say("No entendí el comando. Inténtalo de nuevo.")
    elif command["action"] == "set_time":
        engine.say(f"Ajustando el tiempo a {command['minutes']} minutos.")
    elif command["action"] == "start":
        engine.say("Iniciando el proceso.")
    elif command["action"] == "remove_food":
        engine.say("Sacando la comida.")
    elif command["action"] == "add_food":
        engine.say("Poniendo comida.")
    engine.runAndWait()

    #visual feedback for the user
    return 0

if __name__ == "__main__":
    # Phase 1: keep listening until "inicia el proceso" is heard
    while True:
        recognized_command = speech_recognition()
        if recognized_command and recognized_command["action"] == "start":
            print(f"Comando: {recognized_command}")
            feedback(recognized_command)
            break

    # Phase 2: process started, now accept set_time / add_food / remove_food
    try:
        while True:
            recognized_command = speech_recognition()
            if recognized_command == 0:   # timeout or service error, just listen again
                continue
            print(f"Comando: {recognized_command}")
            feedback(recognized_command)
    except KeyboardInterrupt:
        print("Saliendo...")