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
import webbrowser
import datetime
import pyautogui
from apple_calendar_integration import ICloudCalendarAPI


def there_exists(terms):
    for term in terms:
        if term in voice_data:
            return True

# def monday_speak(text):
#     text = str(text)
#     engine.say(text)
#     engine.runAndWait()

r = sr.Recognizer()
rems = 0
def record_audio(ask=''):
    with sr.Microphone() as source:
        print('Status: Active')
        if rems == 0:
            reminders()
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
        except sr.UnknownValueError:
            pass
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



def respond(voice_data):
    if there_exists(['search for']):
        query = voice_data.split('search for')[1]
        bsearch(query, google=True)
    if there_exists(['open url']):
        query = voice_data.split('open url')[1]
        bsearch(query, url=True)
    if there_exists(['update remote repository']):
        if 'with all files' in voice_data:
            update_remote_repository(voice_data, all=True)
        else:
            update_remote_repository(voice_data)
    if there_exists(['development environment', 'begin work session', 'begin work day']):
        initialize_development_environment()
    
    # greetings, introductions, and pleasantries #
    ##############################################
    
    if there_exists(["thank you","appreciate",]):
        responses = ["You're welcome", 'Indeed']
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)
    if there_exists(['this is monday', 'who are you', 'what are you']):
        monday_speak('I am an Artificial intelligence program. called Monday, however I have only a finite number of executable functinons. All of which are activated by your voice.')
    if there_exists(['hey','hi','hello']):
        greetings = ['hello','hi','I\'m a computer program devoid of what humans call, emotions, formalities are unessesary']
        greet = greetings[random.randint(0, len(greetings)-1)]
        monday_speak(greet)
    if there_exists(["what is your name","what's your name","tell me your name"]):
        monday_speak("I am Monday")
    if there_exists(["how are you","how are you doing"]):
        monday_speak("I exist in 1's and 0's. You do the math. The math is binary - that is, base 2, not base 10 by the way")
    if there_exists(["what's the time","tell me the time","what time is it"]):
        _time = ctime().split(" ")[3].split(":")[0:2]
        if _time[0] == "00":
            hours = '12'
        else:
            hours = _time[0]
        minutes = _time[1]
        _time = hours + " hours and " + minutes + "minutes"
        monday_speak(_time)
    if there_exists(["are you listening","are you on","status","what are you doing"]):
        monday_speak("I am currently in active listening mode 1. awaiting instructions.")

    # Monday program functions & program routines #
    ###############################################

    if there_exists(['open']):
        program = voice_data.split('open')[1]
        open_program(program)

    # Monday program functions & program routines #
    ###############################################

    if there_exists(['update your dependencies file']):
        update_dependancies_file()
    if there_exists(['shut down', 'exit', 'power down', 'initiate shut down']):
        shutdown()
    if there_exists(['standby mode']):
        duration = voice_data.split('for')[1]
        monday_speak(f'Entering stand by mode for {duration}')
        if 'minutes' in duration:
            _len = int(duration.split('minutes')[0]) * 60
            time.sleep(_len)
        if 'seconds' in duration:
            _len = duration.split('seconds')[0]
            time.sleep(_len)
    if there_exists(['restart', 'reboot']):
        reboot()

def bsearch(query, google=False, url=False):
    if google == True:
        google_url = f'https://www.google.com/search?q={query}'
        webbrowser.get().open(google_url)
        monday_speak(f'Searching Google for {query}')
    if url == True:
        url = f'https://www.{query.strip()}'
        webbrowser.get().open(url)
        monday_speak(f'Opening browser for {query}')

def open_program(program):
    monday_speak(f'Opening {program}')
    prog = program.capitalize()
    os.system(f'open /System/Applications/Utilities/{prog}.app')

def task_list():
    '''
    Create a separate calendar for Monday and have it mirror personal cal
    so that creds aren't exposed
    '''
    pass

def archive_contract(*args, **kwargs):
    """Final tear down of completed contract"""
    loc = 'home_server'
    pass

def instantiate_new_conctract():
    """ Create folders and github repository for new contract """
    pass

def appointment_recall():
    """ For appointment level 1(important meetings, etc), vocalize reminder 
        Take appt details and have Monday store in object 
    """
    pass

def initialize_development_environment():
    client_comm_url = 'https://www.upwork.com/messages/'

    monday_speak('Initializing development environment')
    monday_speak('Opening client communication interface')

    webbrowser.get().open(client_comm_url)

def send_file_to_home_server():
    pass

def update_remote_repository(voice_data, all=False):
    if 'message' in voice_data:
        m = voice_data.split('message')[1].split('branch')[0]
        monday_speak(f'Message: {m}')
    else: 
        m = 'Monday Commit'
    if 'branch' in voice_data:
        branch = voice_data.split('branch')[1]
        monday_speak(f'Branch: {branch}')
    else: 
        branch = 'master'
    monday_speak('Updating remote repository.')
    if all == True:
        os.system('git add .')
    else:
        os.system('git add monday.py')
    os.system(f'git commit -m "{m}"')
    os.system(f'git push origin {branch}')
    monday_speak('Done')

def access_config_file():
    """ Access the settings like HOME SERVER so that only this file needs to be
        changed in the event of a move or hardware/software revamp 
        e.g. Local/Public IP, SSH config, Home Server connection settings
    """  


def reminders():
    global rems
    now = datetime.datetime.now()

    if now.hour >= 7 and now.hour <= 10:
        morning_routines(tastk_rem=True)
    else:
        morning_routines()
    rems = rems + 1

def teach(query):
    """
    get text from wikipedia
    """
    pass

def morning_routines(tastk_rem=False):
    today = datetime.date.today()
    monday_speak(f'Today is {today.strftime("%B %d, %Y")}')
    if tastk_rem == True:
        monday_speak('Please don\'t forget to perform India Entertainment search contract. ')

# Monday program routines #
###########################

def reboot():
    monday_speak('Initializing reboot procedures')
    os.system('^C\n' +
              'deactivate\n' +
              'cd /Users/i/Documents/repository/Monday\n' +
              'source venv/bin/activate\n' +
              'python monday.py')


def shutdown():
    monday_speak('Initiating shutdown protocol')
    monday_speak('Deleting temporary audio files')
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)
    monday_speak('Archiving logs.')
    monday_speak('Good day.')
    monday_active = False
    exit()


def update_dependancies_file():
    os.system('pip freeze > requirements.txt')
    monday_speak('Updated requirements.txt with my current library dependancies')

siri_username = 'monday.protocols'
siri_pw = 'zz@ae.q$pNE{(2DS'

time.sleep(1)

monday_active = True
while monday_active:
    voice_data = record_audio()
    respond(voice_data)
