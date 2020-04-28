# monday.py

import speech_recognition as sr
import playsound # to play an audio file
from gtts import gTTS # google text to speech
import random
import os
import time
from time import ctime
import pyttsx3
import subprocess


def there_exists(terms):
    for term in terms:
        if term in voice_data:
            return True

# def monday_speak(text):
#     text = str(text)
#     engine.say(text)
#     engine.runAndWait()

r = sr.Recognizer()

def record_audio(ask=''):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        print('Done Listening')
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
        except sr.UnknownValueError:
            monday_speak('I did not get that')
        except sr.RequestError:
            monday_speak('I can\'t connect to my remote speech recognition servers')
        except sr.WaitTimeoutError:
            monday_speak('I\'m not hearing anything.')
        print('>>', voice_data.lower())
        return voice_data.lower()

def monday_speak(audio_string):
    audio_string = str(audio_string)
    tts = gTTS(text=audio_string, lang='en')
    r = random.randint(1,20000000)
    audio_file = 'audio-' + str(r) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    os.remove(audio_file)

# def say(text):
#     subprocess.call(['say', text])
# say('hello')


def respond(voice_data):
    if there_exists(['hey','hi','hello']):
        greetings = ['hello','hi','I\'m a computer program, formalities are unessesary']
        greet = greetings[random.randint(0, len(greetings)-1)]
        monday_speak(greet)
    if there_exists(["what is your name","what's your name","tell me your name"]):
        monday_speak("I am Monday")
    if there_exists(["how are you","how are you doing"]):
        monday_speak("I exist in 1's and 0's. You do the math. The math is binary - that is, base 2, not base 10, by the way")
    if there_exists(["what's the time","tell me the time","what time is it"]):
        time = ctime().split(" ")[3].split(":")[0:2]
        if time[0] == "00":
            hours = '12'
        else:
            hours = time[0]
        minutes = time[1]
        time = hours + " hours and " + minutes + "minutes"
        monday_speak(time)
    if there_exists(['shut down', 'exit', 'power down', 'initiate shutdown']):
        shutdown()


def archive_contract(*args, **kwargs):
    """Final tear down of completed contract"""
    loc = 'home_server'
    pass

def instantiate_new_conctract():
    """ Create folders and github repository for new contract """
    pass

def appointment_recall():
    """ For appointment level 1(important meetings, etc), vocalize reminder """
    pass

def initialize_development_environment():
    pass

def send_file_to_home_server():
    pass

def update_remote_repository():
    pass

def access_config_file():
    """ Access the settings like HOME SERVER so that only this file needs to be
        changed in the event of a move or hardware/software revamp 
        e.g. Local/Public IP, SSH config, Home Server connection settings
    """  
def shutdown():
    monday_speak('Initiating shutdown protocol.')
    monday_speak('Deleting temporary audio files.')
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)
    monday_speak('ArchIving logs')
    monday_speak('Good day sir. ')
    exit()

time.sleep(1)
# engine = pyttsx3.init()

while 1:
    voice_data = record_audio()
    respond(voice_data)
