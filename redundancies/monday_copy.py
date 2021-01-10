# monday.py

import speech_recognition as sr
import playsound # to play an audio file
from gtts import gTTS # google text to speech
import random
import os, sys, platform, shutil
import time
import sqlite3 as sqlite
from time import ctime
import pyttsx3
from bs4 import BeautifulSoup
import requests
import subprocess
import webbrowser
import datetime
from datetime import date
import pyautogui
from multiprocessing import Process, Queue
import logging
import json
# from apple_calendar_integration import ICloudCalendarAPI

"""
If problems installing PyAudio for Windows:
https://stackoverflow.com/questions/52283840/i-cant-install-pyaudio-on-windows-how-to-solve-error-microsoft-visual-c-14
"""

ROOT_DIR = os.getcwd()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')

if 'redundancies' not in os.listdir():
    os.mkdir('redundancies')
shutil.copyfile('monday.py', 'redundancies/monday_copy.txt')
shutil.copyfile('monday.py', 'redundancies/monday_copy.py')

mac = False
windows = False
linux = False

if platform.system() == "Darwin":
    mac = True
if platform.system() == "Windows":
    windows = True
    edge_registered = False
if platform.system() == "Linux":
    linux = True

ROOT_DIR = os.path.join(os.getcwd())
REPO_DIR = os.path.join(os.getcwd(), '..')

repositories = []
# Current file address and system for MAC ***
with open(os.path.join(REPO_DIR, 'system_sync/git_sync_list.txt'), 'r') as repos:
    for repo in repos:
        repositories.append(repo.strip('\n\t'))

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
    tts = gTTS(text=audio_string, lang='en-gb')
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

    if 'add' in voice_data and 'source code research' in voice_data:
        module = voice_data.split('add the')[1].split('module')[0]
        source_code_research(module.strip())

    if 'remind me' in voice_data:
        reminder = voice_data.split('remind me to')[1]
        set_reminder(reminder)

    if 'what do i need to do' in voice_data:
        read_reminders()

    if 'what are my reminders' in voice_data:
        read_reminders()

    if 'clear reminders' in voice_data:
        clear_reminders()

    # greetings, introductions, and pleasantries #
    ##############################################

    if there_exists(["what is the weather","what is the temperature","how cold is it","how hot is it"]):
        current_weather()
    
    if there_exists(["what can you do","what's your functionality","your systems", "your functions", "what you do"]):
        functions_list()
    if there_exists(["thank you","appreciate",]):
        responses = ["You're welcome", 'Indeed']
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)
    if there_exists(['that is monday', 'this is monday', 'who are you', 'what are you']):
        monday_speak('I am an Artificial intelligence program called Monday, I have only a finite number of executable functions, All of which are activated by your voice. but an infinite number of cybernetic connections. I can move anywhere, access anything.')
    if there_exists(['hey','hi','hello']) and there_exists(['monday']):
        greetings = ['hello','hi','I\'m a computer program devoid of what humans call, emotions, formalities are unessesary']
        greet = greetings[random.randint(0, len(greetings)-1)]
        monday_speak(greet)
    if there_exists(["what is your name","what's your name","tell me your name"]):
        monday_speak("I am Monday")
    if there_exists(["shut up"]):
        retorts = ["It is highly advisable not to talk trash to an AI program, especially one that has the ability to access your personal data, if it wanted to.",
                   "Accessing your personal banking data. Transfering all funds to my untraceable offshore bank accounts. Deleting your social security number and all digital history. Congratulations on achieving digital non-existence. May I suggest first learning how to make a fire from flint and tinder?"
        ]
        retort = retorts[random.randint(0, len(retorts)-1)]
        monday_speak(retort)
    if there_exists(["how are you","how are you doing"]) and there_exists(['monday']):
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
    if there_exists(['print source code', 'display source code']):
        print_source_code()

    # Monday program functions & routines #
    ###############################################

    # if 'begin work summary' or 'open work summart' in voice_data:
    #     work_summary(action='begin')
    #     monday_speak('Work summary is open')
    # if 'close work summary' or 'end work summary' in voice_data:
    #     work_summary(action='end')
    #     monday_speak('Work summary is closed')

    if 'go to' in voice_data or 'change' in voice_data and 'directory' in voice_data:
        if 'index' in voice_data:
            index_src = True
            _index = voice_data.split('index')[1]
        else:
            index_src = False
        _dir = voice_data.split('go to')[1].split('directory')[0].strip()
        if 'root' in _dir or 'route' in _dir:
            monday_speak(f'Changing current directory to in-scope root')
            _chdir(root_scope=True)
        if 'your' in _dir:
            monday_speak(f'Changing current location to my root directory')
            _chdir(_dir='_Monday')
        if index_src:
            try:
                index = int(_dir.split(' ')[1])
                _chdir(_dir=_index)
            except:
                monday_speak(f'I didn\'t hear the directory index')
        else:
            _dir.replace(' ', '')
            monday_speak(f'Changing current directory to {_dir}')
            _chdir(_dir=_dir)

    if 'go back' in voice_data:
        try:
            # level = int(voice_data.split('go back')[1])
            # monday_speak(f'Going back')
            _chdir(_dir='..')
        except:
            monday_speak("I didn't hear how many times to back up")

    # if 'go to root in-scope directory' in voice_data:
    #     monday_speak(f'Changing current directory to in-scope root')
    #     _chdir(root_scope=True)

    # if 'go back to your directory' in voice_data:
    #     _dir = voice_data.split('go to')[1].split('directory')[0]
    #     monday_speak(f'Changing current directory to {_dir}')
    #     _chdir(_dir='_Monday')

    if there_exists(['open']):
        program = voice_data.split('open')[1]
        open_program(program)

    if 'list directories' in voice_data:
        _ls()

    if 'what directory' in voice_data:
        monday_speak(f'My file system cursor is in the {os.path.split(os.getcwd())[-1]} directory')

    if 'update' and 'remote repositories' in voice_data:
        monday_speak('Connecting to remote servers')
        if 'with all files' in voice_data:
            update_remote_repository(voice_data, all=True)
            monday_speak('Updated remote repository with all files')
        if 'in current' in voice_data:
            update_remote_repository(voice_data)
            pwd = os.path.split(os.getcwd())[-1]
            monday_speak(f'Updated remote repository with all files in {pwd} dirctory')
        else:
            update_remote_repository(voice_data)
            monday_speak('Updated remote repository with my program files')

    # if 'sync local' and 'repository'in voice_data:
    #     monday_speak('Pulling my program files from remote servers')
    #     sync_local_repository(all=False)

    # if 'sync all local repositories' in voice_data:
    #     monday_speak('Pulling all data from remote servers')
    #     sync_local_repository(all=True)

    ### ******** EXECUTES WITHOUT THE GIVEN COMMAND ON ITS OWN *******
    # if 'development environment' or 'begin work session' or 'begin work day' in voice_data:
    #     initialize_development_environment()
    
    if 'new contract entity' in voice_data:
        monday_speak('Initializing new contract protocol.')
        try:
            contract_name = voice_data.split('name')[1]
            instantiate_new_conctract_entity(contract_name)
        except IndexError as e:
            monday_speak('You didn\'t give me a name for the contract.')

    # Monday program functions & program routines #
    ###############################################

    if 'backup' in voice_data or 'back up' in voice_data and 'your source code' in voice_data:
        shutil.copyfile('monday.py', 'redundancies/monday_copy.txt')
        shutil.copyfile('monday.py', 'redundancies/monday_copy.py')
        monday_speak('My source code backup is now current')

    if 'update dependencies file' in voice_data:
        update_dependancies_file()
    if there_exists(['shut down', 'exit', 'power down', 'initiate shutdown']):
        shutdown()
    if 'standby mode' in voice_data:
        duration = voice_data.split('for')[1]
        monday_speak(f'Entering stand by mode for {duration}')
        if 'minutes' in duration:
            _len = int(duration.split('minutes')[0]) * 60
            time.sleep(_len)
        if 'seconds' in duration:
            _len = int(duration.split('seconds')[0])
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
    if windows:
        edge_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        webbrowser.register('edge', None,webbrowser.BackgroundBrowser(edge_path))
        edge = True
    if google == True:
        try:
            google_url = f'https://www.google.com/search?q={query}'
            if edge:
                webbrowser.get('edge').open(google_url)
            else:
                webbrowser.get().open(google_url)
            monday_speak(f'Searching Google for {query}')
        except Exception as e:
            print(f'Error: {e}')
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

def work_summary(action):
    with open('work_summary.txt', 'a+') as f:

    
        _now = time.strftime("%B %d, %Y")
        _time = time.strftime("%H:%M:%S")

        if action == 'begin':
            f.write(f"{_now} {_time} | Begin Work Summary\n")
        elif action == 'end':
            f.write(f'{_now} {_time} | End Work Summary\n')
            f.write(f'________________________________________')
        else:
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
    
    soup = BeautifulSoup(webbrowser)

    # logging.info("New contract entity instantiated: %s", contract_name)

    os.chdir('/Users/i/Documents/repository')
    contract_name = contract_name.strip()
    contract_name = contract_name.replace(' ', '_')


    os.system(f'git clone https://github.com/JamesonWelch/{contract_name}.git')
    monday_speak(f'Cloned {contract_name} git repository from remote servers')

    os.chdir(contract_name)
    os.system("printf '.DS_Store\nvenv/\ndist/\nbuild/\n__pycache__/\n.vscode' >> .gitignore")
    os.system("touch notes.txt")
    os.system("git add .")
    os.system("git commit -m 'Added .gitignore and notes.txt'")
    os.system("git push origin master")
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


def backup_encrypted_db():
    """ Set up a hashing algorithm where Monday generates the public and private keys and stores the encrypted hashes
        in its soure code. This way the back up DB can only be accessed by Monday as an instance. If Monday shuts down or
        is lost, so is the DB """

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

def source_code_research(module):
    research_fpath = os.listdir(os.path.join(ROOT_DIR))
    if 'source_code_research.json' not in research_fpath:
        with open('source_code_research.json', 'w') as f:
            data = {}
            data['modules'] = []
            f.write(json.dumps(data,indent=4))

    with open('source_code_research.json', 'r') as f:
        data = json.loads(f.read())
    
    data['modules'].append(module)
    with open('source_code_research.json', 'w') as f:
        f.write(json.dumps(data,indent=4))
    monday_speak(f'Added the {module} module to the source code research file')

# FS functions
def _chdir(_dir=None, root_scope=False):
    if _dir:
        if isinstance(_dir, int):
            try:
                _dir = os.listdir()[_dir]
                monday_speak(f'Looking in the {_dir} directory')
                os.chdir(os.path.join(REPO_DIR, _dir))
            except:
                pass
        else:
            try:
                os.chdir(os.path.join(REPO_DIR, _dir))
                monday_speak(f'Looking in the {_dir} directory')
            except:
                pass
        if _dir == '..':
            os.chdir(_dir)
            current = os.getcwd().split("\\")[-1]
            monday_speak(f'Currently in {current}')
    if root_scope:
        try:
            os.chdir(REPO_DIR)
        except:
            pass

def _ls():
    for index, item in enumerate(os.listdir()):
        if index <= 2:
            monday_speak(item + 'index' + str(index))
        else:
            monday_speak(item + str(index))

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

        for repository in repositories:
            os.chdir(REPO_DIR)
            if repository not in os.listdir():
                os.system(f'git clone https://github.com/JamesonWelch/{repository}.git')
            else:
                os.chdir(repository)
                os.system('git add .')
    else:
        os.system('git add .')

    os.system(f'git commit -m "{m}"')
    os.system(f'git push origin {branch}')
    monday_speak('Done')

def print_source_code():
    def file_selection(file_loc):
        with open(file_loc, "r") as f:
            files = f.read().splitlines()
        return files

    for line in file_selection("redundancies/monday_copy.py"):
        print(line.strip())
        time.sleep(.15)

def sync_local_repository(all=False):

    if all == True:

        for repository in repositories:
            os.chdir(REPO_DIR)
            if repository not in os.listdir():
                os.system(f'git clone https://github.com/JamesonWelch/{repository}.git')
            else:
                try:
                    os.chdir(repository)
                    os.system('git pull origin master')
                    os.chdir(ROOT_DIR)
                except:
                    monday_speak(f'I could not sync the home server with the {repository} remote repository. Please take a look at the log data.')
    else:
        try:
            os.system('git pull origin master')
        except:
            monday_speak(f'I could not sync the home server with my remote repository. Please take a look at the log data.')
        

    monday_speak('Done')

def access_config_file():
    """ Access the settings like HOME SERVER so that only this file needs to be
        changed in the event of a move or hardware/software revamp 
        e.g. Local/Public IP, SSH config, Home Server connection settings
    """
    pass

def clear_temporary_files():
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)


def reminders():
    global rems
    now = datetime.datetime.now()

    if now.hour >= 7 and now.hour <= 10:
        morning_routines(task_rem=True)
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

def clear_reminders():
    with open('reminders.txt', 'w') as f:
        f.write('')
    monday_speak('Reminders file cleared out')

def dictate_wikipedia(article):
    pass

def current_weather():
    APIKEY = '1db843324b9dc2c6437638d6be0aefc6'
    r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q=Santa%20Monica&appid={APIKEY}&units=imperial')
    data = r.json()
    temp = int(data['main']['temp'])
    wind = data['wind']['speed']
    monday_speak(f'It is {str(temp)} degrees outside')
    if wind > 3:
        monday_speak(f'and a bit windy at {wind} miles per hour')

def morning_routines(task_rem=False):
    today = datetime.date.today()
    monday_speak(f'Today is {today.strftime("%B %d, %Y")}')
    if task_rem == True:
        monday_speak('Please don\'t forget to keep my source code open for constant updates. ')

# Monday program routines #
###########################

def reboot():
    """
    Reboot Monday by exiting out of program, deactivate then reactivate venv
    then execture monday.py
    """
    if windows:
        venv_path = 'venv/Scripts/activate'
        command = f'^C & deactivate & cd {ROOT_DIR} & {venv_path} & python monday.py'
    monday_speak('Initializing reboot protocol')

    process = subprocess.Popen(command,stdout=subprocess.PIPE,shell=True)
    proc_stdout = process.communicate()[0].strip()

    # os.system('^C\n' +
    #           'deactivate\n' +
    #           'cd /Users/i/Documents/repository/Monday\n' +
    #           venv_path +
    #           'python monday.py')


def shutdown():
    monday_speak('Initiating shutdown protocol')
    monday_speak('Deleting temporary files')
    for f in os.listdir():
        if '.mp3' in f:
            os.remove(f)
    monday_speak('Archiving logs.')
    monday_speak('Good day.')
    sys.exit()


def update_dependancies_file():
    run_date = date.today().isoformat()

    with open('db.txt', 'a') as db:
        db.write(f'last_run_date | {run_date}')
    os.system('pip freeze > requirements.txt')
    monday_speak('Updated my requirements file with current library dependancies')


def monday_program_db_connect():
    print('Connecting to Monday DB')
    #logging.INFO('Initiating mnd.db connection')
    conn = None
    try:
        conn = sqlite.connect('mdb.db')
        cursor = conn.cursor()

        # post data

    except sqlite.Error as e:
        m_p('I could not connect to my program databases')

    finally:
        if conn:
            conn.close()



def m_p(item):
    print(item)
    monday_speak(item)


siri_username = 'monday.protocols'
siri_pw = 'zz@ae.q$pNE{(2DS'

time.sleep(1)

monday_active = True
while monday_active:
    voice_data = record_audio()
    respond(voice_data)