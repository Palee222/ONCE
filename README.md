# ONCE

Hi Milan, Farah and Aitana!

You can find here the requested voice command code for the kinova arm. The code can give visual, audio and textual feedback. You can test it yourself too. Please let me know if I should change anything during the weekend!

Thanks,

    Laura

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
