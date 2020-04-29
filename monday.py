# monday.py

import speech_recognition as sr
import playsound # to play an audio file
from gtts import gTTS # google text to speech
import random
import os, sys
import time
from time import ctime
import pyttsx3
import subprocess
import webbrowser
import datetime
import pyautogui
from multiprocessing import Process, Queue
import logging
from apple_calendar_integration import ICloudCalendarAPI


ROOT_DIR = os.getcwd()

# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.DEBUG,
#     datefmt='%Y-%m-%d %H:%M:%S')


def there_exists(terms):
    for term in terms:
        if term in voice_data:
            return True


def timeout(seconds, action=None):
    """Calls any function with timeout after 'seconds'.
       If a timeout occurs, 'action' will be returned or called if
       it is a function-like object.
    """
    def handler(queue, func, args, kwargs):
        queue.put(func(*args, **kwargs))

    def decorator(func):

        def wraps(*args, **kwargs):
            q = Queue()
            p = Process(target=handler, args=(q, func, args, kwargs))
            p.start()
            p.join(timeout=seconds)
            if p.is_alive():
                p.terminate()
                p.join()
                if hasattr(action, '__call__'):
                    return action()
                else:
                    return action
            else:
                return q.get()

        return wraps

    return decorator


# def monday_speak(text):
#     text = str(text)
#     engine.say(text)
#     engine.runAndWait()

r = sr.Recognizer()
rems = 0
def record_audio(ask=False):
    with sr.Microphone() as source:
        today = datetime.date.today()
        time.ctime()
        print(f'Status: Active | Current Time: {time.strftime("%H:%M")} {today.strftime("%B %d, %Y")}')

        if ask:
            print(ask)

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
    os.chdir(ROOT_DIR)
    if there_exists(['search for']):
        query = voice_data.split('search for')[1]
        bsearch(query, google=True)
    if there_exists(['open url']):
        query = voice_data.split('open url')[1]
        bsearch(query, url=True)

    if 'remind me' in voice_data:
        reminder = voice_data.split('remind me to')[1]
        set_reminder(reminder)

    if 'what do i need to do' in voice_data:
        read_reminders()

    # greetings, introductions, and pleasantries #
    ##############################################
    
    if there_exists(["what can you do","what's your functionality","your systems", "your functions", "what you do"]):
        functions_list()
    if there_exists(["thank you","appreciate",]):
        responses = ["You're welcome", 'Indeed']
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)
    if there_exists(['this is monday', 'who are you', 'what are you']):
        monday_speak('I am an Artificial intelligence program. called Monday, however I have only a finite number of executable functions. All of which are activated by your voice.')
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

    # Monday program functions & routines #
    ###############################################

    if there_exists(['open']):
        program = voice_data.split('open')[1]
        open_program(program)

    if there_exists(['update remote repository']):
        monday_speak('Connecting to remote servers')
        if 'with all files' in voice_data:
            update_remote_repository(voice_data, all=True)
            monday_speak('Updated remote repository with all files')
        else:
            update_remote_repository(voice_data)
            monday_speak('Updated remote repository with my program file')

    if there_exists(['development environment', 'begin work session', 'begin work day']):
        initialize_development_environment()
    
    if 'new contract entity' in voice_data:
        monday_speak('Initializing new contract protocol.')
        try:
            contract_name = voice_data.split('name')[1]
            instantiate_new_conctract_entity(contract_name)
        except IndexError as e:
            monday_speak('You didn\'t give me a name for the contract.')

    # Monday program functions & program routines #
    ###############################################

    if there_exists(['update dependencies file']):
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


    if there_exists(['remove', 'delete','clear']) and there_exists(['temporary files', 'audio files']):
        clear_temporary_files()
        monday_speak('temporary files removed')

    if there_exists(['how many']) and there_exists(['files']):
        a_f = [x for x in os.listdir() if x.endswith('.mp3')]
        monday_speak(f'I have {len(a_f)} audio files in my program folder.')



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

def master_repo_list():
    pass

def compile_master_repositorty_list():
    pass

def sync_local_repositories():
    pass

def archive_contract(*args, **kwargs):
    """Final tear down of completed contract"""
    loc = 'home_server'
    pass
#________________________________________________________________________________________________________
# @timeout(600)
def instantiate_new_conctract_entity(contract_name):
    """ Create folders and github repository for new contract """

    # NEED TO CREATE BRIEF DESCRIPTION FOR MONDAY ARCHIVE - QUICKLY RETRIEVE PREVIOUS CODE BE KEYWORD
    # MONDAY ARCHIVE = NAME, BRIEF DESCRIPTION, REPO URL

    monday_speak('Opening browser. Tell me when you are done.')
    webbrowser.get().open('https://github.com/new')
    time.sleep(20)
        
    # logging.info("New contract entity instantiated: %s", contract_name)

    os.chdir('/Users/i/Documents/repository')
    contract_name = contract_name.strip()
    contract_name = contract_name.replace(' ', '_')


    os.system(f'git clone https://github.com/JamesonWelch/{contract_name}.git')
    monday_speak(f'Cloned {contract_name} git repository from remote servers')

    os.chdir(contract_name)
    os.system("printf '.DS_Store\nvenv/\ndist/\nbuild/' >> .gitignore")
    monday_speak('git ignore file created')

    #if os == 'mac':...
    try:
        os.system('virtualenv venv')
    except:
        pass
    

def functions_list():
    monday_speak('I have a range of functions I can perform. While many of those functions can be used in any situation,'
                 'most of my capabilities center around digital systems and data pipeline development. '
                 'My functions of a more general nature include telling the time, describing who and what I am, '
                 'perform Google searches and visit websites, as well as conveying'
                 'basic systems diagnostics and protocol levels. I can even reboot and shut down my system.'
                 'Regarding functions that pertain to why I exist, I can update remote repository servers and clone them if need be.'
                 'When a new client is acquired, I can set up the entire development environment save for creating the remote repository'
                 'because this function necessitates the use of private credentials. This means that all the folders, files, virtual'
                 'environments, and git ignore files will be created. I stay busy.'
    )


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

def clear_temporary_files():
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)


def reminders():
    global rems
    now = datetime.datetime.now()

    if now.hour >= 7 and now.hour <= 10:
        morning_routines(tastk_rem=True)
    else:
        morning_routines()
    rems = rems + 1

def set_reminder(reminder):
    monday_speak(f'adding {reminder} to reminders file')
    with open('reminders.txt', 'a') as f:
        f.write(reminder + ', ')

def read_reminders():
    reminders_list = []
    with open('reminders.txt', 'r') as f:
        for line in f:
            reminders_list.append(line)
    monday_speak(f'You need to {reminders_list}')

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
    monday_speak('Initializing reboot protocol')
    os.system('^C\n' +
              'deactivate\n' +
              'cd /Users/i/Documents/repository/Monday\n' +
              'source venv/bin/activate\n' +
              'python monday.py')


def shutdown():
    monday_speak('Initiating shutdown protocol')
    monday_speak('Deleting audio files')
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)
    monday_speak('Archiving logs.')
    monday_speak('Good day.')
    sys.exit()


def update_dependancies_file():
    os.system('pip freeze > requirements.txt')
    monday_speak('Updated my requirements file with current library dependancies')


siri_username = 'monday.protocols'
siri_pw = 'zz@ae.q$pNE{(2DS'

time.sleep(1)

monday_active = True
while monday_active:
    voice_data = record_audio()
    respond(voice_data)
