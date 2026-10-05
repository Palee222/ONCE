import numpy as np
import os
import re
import unicodedata
import threading
import queue
import tkinter as tk

#!/usr/bin/env python3

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
        "iniciar el proceso": "start",
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
class StatusWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Estado del brazo")
        self.canvas = tk.Canvas(self.root, width=220, height=110, highlightthickness=0)
        self.canvas.pack(padx=20, pady=(20, 5))
        self.red = self.canvas.create_oval(10, 10, 100, 100, fill="#ff0000")
        self.green = self.canvas.create_oval(120, 10, 210, 100, fill="#003300")
        self.label = tk.Label(self.root, text="Esperando...", font=("Helvetica", 16))
        self.label.pack(pady=(5, 20))
        self.updates = queue.Queue()
        self.root.after(100, self._poll)

    def set_state(self, busy, text):
        # safe to call from the listening thread
        self.updates.put((busy, text))

    def _poll(self):
        while not self.updates.empty():
            busy, text = self.updates.get()
            self.canvas.itemconfig(self.red, fill="#550000" if busy else "#ff0000")
            self.canvas.itemconfig(self.green, fill="#00cc00" if busy else "#003300")
            self.label.config(text=text)
        self.root.after(100, self._poll)
        
def feedback(command, window):
    #give visual and audio feedback on starting the process, setting the minutes to x and putting/taking food
    '''
    The visual feedback would be just a UI with a red and green lamp. The red turns on when the arm is doing nothing and green turns on when the arm understood the command and is in the process
    of doing it. Also, there would be a text feedback like "Doing the process...".
    
    For audio feedback it would be almost the same, just feedback is being said. For example, "Setting time for x minutes" or "Starting process".
    '''
    
        #visual feedback for the user
    if command is None:
        window.set_state(False, "No entendí el comando")
    elif command["action"] == "set_time":
        window.set_state(True, f"Ajustando el tiempo a {command['minutes']} minutos...")
    elif command["action"] == "start":
        window.set_state(True, "Iniciando el proceso...")
    elif command["action"] == "remove_food":
        window.set_state(True, "Sacando la comida...")
    elif command["action"] == "add_food":
        window.set_state(True, "Poniendo comida...")
        
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

    window.set_state(False, "Esperando...")   # back to red when done
    return 0

MESSAGES = {
    "start": "Iniciar el proceso",
    "remove_food": "Sacando la comida",
    "add_food": "Poniendo comida",
}

def describe(command):
    if command["action"] == "set_time":
        return f"Ajustando el tiempo a {command['minutes']} minutos"
    return MESSAGES[command["action"]]


def send_to_arm(command):
    # TODO: connect to the arm here (serial, GPIO, ROS, etc.)
    # command looks like {"action": "start"} or {"action": "set_time", "minutes": 5}
    print(f"[ARM] {command}")


def speak(text):
    engine.say(text)
    engine.runAndWait()


def run_assistant(window):
    # 1. Listen until "inicia el proceso" is heard
    while True:
        command = speech_recognition()
        if command and command["action"] == "start":
            break

    # 2. Light green, announce, and the arm puts the food in the microwave
    window.set_state(True, "Poniendo comida en el microondas...")
    speak("Iniciando el proceso")
    send_to_arm({"action": "add_food"})   # must wait until the arm is done
    window.set_state(True, "Comida dentro. Di el tiempo...")
    speak("Comida dentro. ¿Cuántos minutos?")

    # 3. Wait for the time command ("ajusta el tiempo a X minutos")
    while True:
        command = speech_recognition()
        if command == 0:                    # timeout / service error, listen again
            continue
        if command is None:                 # not understood, or time outside 1-35
            speak("No entendí el tiempo. Inténtalo de nuevo.")
            continue
        if command["action"] == "set_time":
            break                           # ignore any other command

    # 4. Set the time on the microwave
    window.set_state(True, f"Ajustando el tiempo a {command['minutes']} minutos...")
    speak(f"Ajustando el tiempo a {command['minutes']} minutos")
    send_to_arm(command)
    window.set_state(True, "Proceso en marcha...")


if __name__ == "__main__":
    window = StatusWindow()
    threading.Thread(target=run_assistant, args=(window,), daemon=True).start()
    window.root.mainloop()