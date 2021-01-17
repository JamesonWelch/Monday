# monday.py

import speech_recognition as sr
import playsound # to play an audio file
from gtts import gTTS # google text to speech
import speech_config
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


with open('master_config.json', 'r') as f:
    config = json.loads(f.read())

ROOT_DIR = os.getcwd()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.ERROR,
    datefmt='%Y-%m-%d %H:%M:%S')

if 'redundancies' not in os.listdir():
    os.mkdir('redundancies')
shutil.copyfile('monday.py', 'redundancies/monday_copy.txt')
shutil.copyfile('monday.py', 'redundancies/monday_copy.py')

prog_start = time.time()

mac = False
windows = False
linux = False

if platform.system() == "Darwin":
    mac = True
if platform.system() == "Windows":
    windows = True
    edge_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    webbrowser.register('edge', None,webbrowser.BackgroundBrowser(edge_path))
    edge_registered = True
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

# Globals
rems = 0
time_lap = None
reminded = False
work_start = time.time()
verbose = False
mute = False

def receive_command(ask=False):
    with sr.Microphone() as source:
        global reminded
        today = datetime.date.today()
        time.ctime()
        if format(datetime.datetime.now(), '%H:%M') == time_lap and reminded == False:
            cron()
            reminded = True
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
            monday_speak('I am unable to connect to my speech recognition servers')
        except sr.WaitTimeoutError:
            monday_speak('I\'m not hearing anything.')
        print('>>', voice_data.lower())
        return voice_data.lower()

def monday_speak(audio_string):
    global mute
    if verbose:
        print(audio_string)
    if not mute:
        audio_string = str(audio_string)
        tts = gTTS(text=audio_string, lang='en-gb')
        r = random.randint(1,20000000)
        audio_file = 'audio-' + str(r) + '.mp3'
        tts.save(audio_file)
        playsound.playsound(audio_file)
        os.remove(audio_file)
    elif mute:
        print(audio_string)

def response_polarity(voice_data):
    if voice_data in speech_config.deny:
        return '-'
    if  voice_data in speech_config.affirm:
        return '+'

def exec_stdout(cmd, module='os') -> str:
    """ Execute command with stdout capture option """
    if module == 'os' and isinstance(cmd,str):
        os.system(cmd)
    elif module == 'subprocess' or isinstance(cmd,list):
        _out = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
        _out = _out.decode('utf-8')
        print(_out)
        return _out

def analyze_response(response_data, os_output):
    if response_data in os_output:
        return True
    else:
        return False

def update_config():
    with open('master_config.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(config))
    

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
    if program == 'code editor':
        os.system('code .')
        monday_speak(f'Opening V S Code')
    else:
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
    if windows:
        webbrowser.get('edge').open('https://github.com/new')
    if mac:
        webbrowser.get().open('https://github.com/new')
    time.sleep(20)
    
    # soup = BeautifulSoup(webbrowser)

    logging.info("New contract entity instantiated: %s", contract_name)

    os.chdir(REPO_DIR)
    contract_name = contract_name.strip()
    contract_name = contract_name.replace(' ', '_')


    os.system(f'git clone https://github.com/JamesonWelch/{contract_name}.git')
    monday_speak(f'Cloned {contract_name} git repository from remote servers')

    gitignore_append = ['# Misc','.DS_Store','venv','dist','build','__pycache__','.vscode',]

    os.chdir(contract_name)
    if mac:
        os.system("printf '.DS_Store\nvenv/\ndist/\nbuild/\n__pycache__/\n.vscode' >> .gitignore")
        os.system("touch notes.txt")
    if windows:
        for ignore in gitignore_append:
            os.system(f"echo {ignore} >> .gitignore")
        os.system("type null notes.txt")

    os.system("git add .")
    os.system("git commit -m 'Added .gitignore and notes.txt'")
    os.system("git push origin main")
    monday_speak('git ignore file created')

    #if os == 'mac':...
    try:
        os.system('virtualenv venv')
    except:
        pass
    
    if windows:
        os.system("venv/Scripts/activate.bat")
        os.system('code .')

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

def begin_work_session():
    global time_lap
    global reminded
    reminded = False
    
    time_lap = format(datetime.datetime.now() + datetime.timedelta(hours=1), '%H:%M')
    monday_speak('Got it')

def work_session_duration():
    global time_lap
    global reminded
    global work_start

    if reminded == False:
        dur = round((time.time() - work_start)/60)
        responses = [f'Work session status, {dur} minutes', 
                     f'You have been working uninterrupted for {dur} minutes',
                     f'Current Work session duration, {dur} minutes',]
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)
        monday_speak(f'Work session status {dur} minutes')


def cron():
    responses = ['It has been an hour since you started work. Perhaps a break is necessary','You have been working for an hour now.', 'You have been working for one hour. Longevity is key',]
    response = responses[random.randint(0, len(responses)-1)]
    monday_speak(response)

def initialize_development_environment():

    client_comm_url = 'https://www.upwork.com/messages/'

    monday_speak('Initializing development environment')
    monday_speak('Opening client communication interface')

    webbrowser.get().open(client_comm_url)

def send_file_to_home_server():
    pass

def metadata_query():
    dir_contents = os.listdir()
    for item in dir_contents:
        filename, file_ext = os.path.splitext(item)
        if file_ext == '.json':
            if filename == 'dataset':
                with open(item, 'r') as f:
                    data = json.loads(f.read())
                _len = len(data)
                filesize = os.stat(item).st_size
                return (_len, filesize)

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
                i_dir = os.listdir()[_dir]
                monday_speak(f'Looking in the {i_dir} directory')
                os.chdir(i_dir)
            except:
                pass
        else:
            if _dir == '_Monday':
                os.chdir(os.path.join(REPO_DIR, '_Monday'))
            else:
                try:
                    os.chdir(_dir)
                    monday_speak(f'Looking in the {_dir} directory')
                except:
                    pass
        if _dir == '..':
            os.chdir(_dir)
            current = os.path.split(os.getcwd())[-1]
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
        monday_speak(f'Attempting digital hand shake with the {branch} branch')
    else: 
        branch = 'master'
    if all == True:

        for repository in os.listdir(REPO_DIR):
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

def git_push(branch=None, message=None):
    current = os.path.split(os.getcwd())[-1]
    if not branch:
        if current not in config['git']['repository']:
            _stdout = exec_stdout(['git', 'branch', '-vv'])
            branch = _stdout.split()[1]
            config['git']['repository'].update({current:{'origin':branch}})
            update_config()
            monday_speak(f'updated the {current} repository configuration file with the {branch} origin branch')
        elif current in config['git']['repository']:
            branch = config['git']['repository'][current]['origin']

    if message:
        message = message
    elif not message:
        message = 'Monday push'
    os.system('git add .')
    os.system(f'git commit -m "{message}"')
    os.system(f'git push origin {branch}')
    monday_speak(f'Updated remote servers with the {current} repository')

def git_pull(branch=None):
    current = os.path.split(os.getcwd())[-1]
    if not branch:
        if current not in config['git']['repository']:
            _stdout = exec_stdout(['git', 'branch', '-vv'])
            branch = _stdout.split()[1]
            config['git']['repository'].update({current:{'origin':branch}})
            update_config()
            monday_speak(f'updated the {current} repository configuration file with the {branch} origin branch')
        elif current in config['git']['repository']:
            branch = config['git']['repository'][current]['origin']

    os.system(f'git pull origin {branch}')
    monday_speak(f'Pulled remote server files from the {current} repository')

def print_source_code():
    def file_selection(file_loc):
        with open(file_loc, "r") as f:
            files = f.read().splitlines()
        return files
    source_code_path = os.path.join(ROOT_DIR,"redundancies/monday_copy.py")
    for line in file_selection(source_code_path):
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

def end_of_day():
    #Stocks
        # ARK trading, current share price info
    # News headlines
    # work hours
    # Completed tasks versus incomplete tasks

    pass

def set_monday_feature_item(feature):
    features_queue = os.path.join(ROOT_DIR, 'monday_feature_queue.txt')
    monday_speak(f'adding {feature} to monday feature queue')
    with open(features_queue, 'a') as f:
        f.write(feature + ',')

def read_monday_feature_queue(_random=False):
    reminder_path = os.path.join(ROOT_DIR, 'monday_feature_queue.txt')
    features_queue = []
    with open(reminder_path, 'r') as f:
        features = f.read()
        for line in features.split(','):
            features_queue.append(line)
    print(features_queue)
    if _random:
        response = random.choice(features_queue)
        monday_speak(f'you could update my system features by attending to the queue. how about {response}')
        return
    if len(features_queue) > 0:
        if len(features_queue) == 1:
            monday_speak(f'You need to build the functionality for {features_queue}')
        if len(features_queue) > 1:
            # temp_reminders = reminders_list
            # temp_reminders.insert(-1, 'and')
            monday_speak(f'You need to build the functionality for {features_queue}')
    else:
        monday_speak(f'I have nothing for you to do')

def reminders():
    global rems
    now = datetime.datetime.now()

    if now.hour >= 7 and now.hour <= 10:
        morning_routines(task_rem=True)
    else:
        morning_routines()
    rems = rems + 1

def set_reminder(reminder):
    reminder_path = os.path.join(ROOT_DIR, 'reminders.txt')
    monday_speak(f'adding {reminder} to reminders file')
    with open(reminder_path, 'a') as f:
        f.write(reminder + ',')

def read_reminders():
    reminder_path = os.path.join(ROOT_DIR, 'reminders.txt')
    reminders_list = []
    with open(reminder_path, 'r') as f:
        rems = f.read()
        for line in rems.split(','):
            reminders_list.append(line)
    if len(reminders_list) > 0:
        if len(reminders_list) == 1:
            monday_speak(f'You need to {reminders_list}')
        if len(reminders_list) > 1:
            # temp_reminders = reminders_list
            # temp_reminders.insert(-1, 'and')
            monday_speak(f'You need to {reminders_list}')
    else:
        monday_speak(f'I have nothing for you to do')

def clear_reminders():
    reminder_path = os.path.join(ROOT_DIR, 'reminders.txt')
    with open(reminder_path, 'w') as f:
        f.write('')
    monday_speak('Reminders file cleared out')

def dictate_wikipedia(article):
    pass

def log_activity(activity):
    activity_path = 'activity_log.json'
    today = str(datetime.date.today())

    if activity_path not in os.listdir():
        with open(activity_path, 'w') as outfile:
            data = []
            outfile.write(json.dumps(data))

    with open(activity_path, 'r') as f:
        data = json.loads(f.read())
    if today in data:
        data[today].append(activity)
    else:
        data.append({today : [activity]})

    with open(activity_path, 'w') as outfile:
        outfile.write(json.dumps(data))

def current_weather():
    APIKEY = '1db843324b9dc2c6437638d6be0aefc6'
    r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q=Santa%20Monica&appid={APIKEY}&units=imperial')
    data = r.json()
    temp = int(data['main']['temp'])
    wind = data['wind']['speed']
    monday_speak(f'It is {str(temp)} degrees outside')
    if wind > 10:
        monday_speak(f'and a bit windy at {wind} miles per hour')

def time_of_day():
    today = datetime.date.today()
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour <= 11:
        return 'morning'
    if hour >= 12 and hour <= 17:
        return 'afternoon'
    elif hour >= 18 and hour <= 23:
        return 'evening'

def morning_routines(task_rem=False):
    today = datetime.date.today()
    monday_speak(f'good {time_of_day()}')
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
    voice_data = receive_command()

    if there_exists(['search']):
        if 'search for' in voice_data:
            query = voice_data.split('search for')[1]
        if 'search stack overflow' in voice_data:
            query = voice_data.split('search stack overflow')[1]
            bsearch(query, url=True)
        else:
            query = voice_data.split('search')[1]
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

    if 'add' and 'to monday feature list' in voice_data:
        feature = voice_data.split('add')[1].split('to monday feature list')[0]
        set_monday_feature_item(feature)

    if there_exists(['monday features queue','monday features q','monday features que']):
        monday_speak('Getting Monday features queue')
        read_monday_feature_queue()

    # greetings, introductions, and pleasantries #
    ##############################################

    if there_exists(["what is the weather","what is the temperature","how cold is it","how hot is it"]):
        current_weather()
    
    if there_exists(["what can you do","what's your functionality","your systems", "your functions", "what you do"]):
        functions_list()
    if there_exists(["thank you","appreciate","thanks"]):
        responses = ["You're welcome", 'Indeed']
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)
    if there_exists(['that is monday', 'this is monday', 'who are you', 'what are you']):
        monday_speak('I am an Artificial intelligence program called Monday, I have only a finite number of executable functions, All of which are activated by your voice. but an infinite number of cybernetic connections. I can move anywhere, access anything.')
    if there_exists(['hey','hi','hello']) and there_exists(['monday']):
        greetings = ['hello','hi','I am a computer program devoid of what humans call emotions, formalities are unnecessary']
        greet = greetings[random.randint(0, len(greetings)-1)]
        monday_speak(greet)
    if there_exists(["what is your name","what's your name","tell me your name"]):
        monday_speak("I am Monday")
    if there_exists(["shut up"]):
        retorts = ["It is highly advisable not to talk trash to an AI program, especially one that has the ability to access your personal data, if it wanted to.",
                   "Accessing your personal banking data. Transfering all funds to my untraceable offshore bank accounts. Deleting your social security number and all digital history. Congratulations on achieving digital non-existence. May I suggest first learning how to make a fire from flint and tinder"
        ]
        retort = retorts[random.randint(0, len(retorts)-1)]
        monday_speak(retort)

    if there_exists(['hurry up', 'go faster', 'what is taking so long']):
        responses = ['perhaps increasing your equipment budget would eliminate your bottle neck', 'i can only work with the provided technology. get better stuff.','upgrade my hardware then we can talk']
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)

    if there_exists(['should i keep working']):
        hour = datetime.datetime.now().hour
        if hour >= 0 and hour <= 11:
            response = 'Yes'
        if hour >= 12 and hour <= 17:
            response = 'Yes'
        elif hour >= 18 and hour <= 23:
            response = 'Maybe you should keep working. Or not. But since it is evening why not grab a glass of bullet neat. I say neat because you clearly have not heeded Laurens advice about the big ice cube'
        monday_speak(f'{response}')

    if there_exists(['what should i do', 'i don\'t know what to do']):
        read_monday_feature_queue(_random=True)
        cm_res = receive_command()
        if 'not that one' in cm_res:
            monday_speak('Then do what you want')

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
    if there_exists(["are you listening","are you on","listening status","what are you doing"]):
        monday_speak("I am currently in active listening mode 1. awaiting instructions.")
    if there_exists(['print your source code', 'display your source code', 'show your source code']):
        print_source_code()

    if there_exists(['mute']):
        mute = True

    if there_exists(['unmute']):
        mute - False
        
    if there_exists(['how long have you been active', 'what is your up time']):
        uptime = (time.time() - prog_start) / 60
        if uptime < 60:
            monday_speak(f'My systems have been active for {round(uptime,2)} minutes')
        elif uptime > 60:
            uptime = int(uptime/60)
            if uptime > 1:
                hour = 'hours'
            elif uptime == 1:
                hour = 'hour'
            frac = uptime % 60
            monday_speak(f'My systems have been active for {uptime} {hour} and {round(frac,1)} minutes')

    if there_exists(['i\'m going out', 'i\'m leaving', 'i\'m heading out', 'i\'m going']):
        monday_speak('do i need to shut down or go into stasis?')
        cm_res = receive_command()
        if response_polarity(cm_res) == '-':
            responses = ['have a great time sir', f'enjoy your {time_of_day()} sir',]
            response = responses[random.randint(0, len(responses)-1)]
            monday_speak(response)
        else:
            if 'shut down' in cm_res:
                shutdown()
            elif 'stasis' in cm_res:
                duration = cm_res.split('for')[-1].split('minutes')[0]
                monday_speak(f'entering stasis for {duration} minutes')
                time.sleep(int(duration)*60)

    if there_exists(['beginning workflow', 'starting work session', 'sitting down for work', 'start work']):
        begin_work_session()

    if there_exists(['how long have i been working', 'work session length', 'when is my next break', 'work session duration', 'work session status']):
        work_session_duration()

    if there_exists(['log activity']):
        activity = voice_data.split('log activity')[-1].split()[0]
        log_activity(activity)
        monday_speak(f'{activity} activity logged')
        

    # if there_exists(['verbose set to true', 'set verbose to true', 'set verbose preference to true', 'verbose mode 1', 'verbose level 1']):
    #     global verbose
    #     verbose = True
    #     monday_speak('Verbose setting activated')

    # if there_exists(['verbose set to false', 'set verbose to false', 'set verbose preference to false', 'verbose mode 0', 'verbose level 0']):
    #     verbose = False
    #     monday_speak('Verbose setting deactivated')

    # Monday program functions & routines #
    ###############################################

    # if 'begin work summary' or 'open work summart' in voice_data:
    #     work_summary(action='begin')
    #     monday_speak('Work summary is open')
    # if 'close work summary' or 'end work summary' in voice_data:
    #     work_summary(action='end')
    #     monday_speak('Work summary is closed')

    if there_exists(['how much data', 'how many data points', 'data status']):
        _len  = metadata_query()[0]
        filesize = metadata_query()[1]
        monday_speak(f'I have collected {_len} data points at a size of {filesize} bytes')

    if there_exists(['start program timer']):
        pass

    if 'directory contents and indexes' in voice_data:
        for index, item in enumerate(os.listdir()):
            print(item, ' ', index)
        monday_speak('Current directory contents and indexes are displayed in my terminal standard out')

    if 'go to' in voice_data and 'directory' in voice_data:
        if 'the' in voice_data:
            ''.join(voice_data.split('the'))
        _dir = voice_data.split('go to')[1].split('directory')[0].strip()
        if 'your' in _dir:
            monday_speak(f'Changing current location to my root directory')
            _chdir(_dir='_Monday')
        elif 'index' in voice_data:
            index_src = True
            _index = voice_data.split('index')[1]
            if 'for' in _index:
                _index = 4
            try:
                # index = int(_dir.split(' ')[1])
                _chdir(_dir=int(_index))
            except Exception as e:
                print(e)
                monday_speak(f'I didn\'t hear the directory index')
        elif 'repository' in _dir:
            monday_speak(f'Changing current directory to in-scope root')
            _chdir(root_scope=True)
        
        else:
            _dir.replace(' ', '')
            monday_speak(f'Changing current directory to {_dir}')
            _chdir(_dir=_dir)

    # if 'go to repository directory' in voice_data:
    #     _chdir(root_scope=True)

    if 'go back one level' in voice_data:
        try:
            # level = int(voice_data.split('go back')[1])
            # monday_speak(f'Going back')
            os.chdir('..')
            monday_speak(f'Currently in {os.path.split(os.getcwd())[-1]}')
        except Exception as e:
            print(e)
            monday_speak("I didn't hear how many times to back up")

    # if 'go to root in-scope directory' in voice_data:
    #     monday_speak(f'Changing current directory to in-scope root')
    #     _chdir(root_scope=True)

    # if 'go back to your directory' in voice_data:
    #     _dir = voice_data.split('go to')[1].split('directory')[0]
    #     monday_speak(f'Changing current directory to {_dir}')
    #     _chdir(_dir='_Monday')

    if there_exists(['open']):
        if 'code editor' in voice_data:
            program = 'code editor'
        else:
            program = voice_data.split('open')[1]
        open_program(program)

    if 'list directories' in voice_data:
        _ls()

    if 'what directory' in voice_data:
        monday_speak(f'My file system cursor is in the {os.path.split(os.getcwd())[-1]} directory')

    # if 'update' in voice_data and 'remote repositories' in voice_data or 'remote repository' in voice_data:
    #     monday_speak('Connecting to the remote servers')
    #     if 'with all files' in voice_data:
    #         update_remote_repository(voice_data, all=True)
    #         monday_speak('Updated remote repository with all files')
    #     if 'in current' in voice_data:
    #         update_remote_repository(voice_data)
    #         pwd = os.path.split(os.getcwd())[-1]
    #         monday_speak(f'Updated remote repository with all files in {pwd} dirctory')
    #     else:
    #         update_remote_repository(voice_data)
    #         monday_speak('Updated remote repository with my program files')

    if 'push local repository' in voice_data:
        if 'message' in voice_data:
            message = voice_data.split('message')[-1]
            monday_speak('With default origin branch?')
            cm_res = receive_command()
            if 'yes' in cm_res:
                monday_speak('Connecting to remote servers')
                git_push(message=message)
            elif 'no' in cm_res or 'the' in cm_res:
                cm_res = cm_res.split('no')[-1]
                cm_res = cm_res.split('the')[-1]
                branch = cm_res.split('branch')[-1]
                monday_speak('Connecting to remote servers')
                git_push(branch, message)
            else:
                monday_speak('Connecting to remote servers')
                git_push(message=message)
        
        elif 'branch' in voice_data:
            branch = voice_data.split('branch')[-1]
            if branch == 'maine':
                branch = 'main'
            monday_speak('What is the message parameter')
            cm_res = receive_command()
            if 'generic' in cm_res or 'doesn\'t matter' in cm_res:
                monday_speak('Got it')
                monday_speak('Connecting to remote servers')
                git_push(branch)
            else:
                monday_speak('Received')
                monday_speak('Connecting to remote servers')
                git_push(branch,cm_res)
        else:
            git_push()

    if there_exists(['pull remote repository']):
        monday_speak('Importing from git servers')
        if 'branch' in voice_data:
            branch = voice_data.split('branch')[-1]
            git_pull(branch=branch)
        else:
            git_pull()
        monday_speak('Local repository now synchronized')
        
        # git_pull()
        # os.system(f'git pull origin {branch}')

    if there_exists(['git status', 'repository status']):
        if 'working tree clean' in exec_stdout(['git', 'status']):
            monday_speak('branch up to date')
            
        os.system('git status')
        monday_speak("Repository status in my terminal")

    # if 'open code editor' in voice_data:
    #     if windows:
    #         os.system('code .')
    #     monday_speak(f'Opening V S Code ')

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

    if 'start new repository' in voice_data:
        monday_speak('Initializing new entity protocol.')
        try:
            contract_name = voice_data.split('name')[1]
            instantiate_new_conctract_entity(contract_name)
        except IndexError as e:
            monday_speak('You didn\'t give me a name for the contract.')

    # Monday program functions & program routines #
    ###############################################

    if 'backup' in voice_data or 'back up' in voice_data and 'your source code' in voice_data:
        monday_source_code = os.path.join(ROOT_DIR,'monday.py')
        txt_backup_path = os.path.join(ROOT_DIR,'redundancies/monday_copy.txt')
        py_backup_path = os.path.join(ROOT_DIR,'redundancies/monday_copy.py')
        shutil.copyfile(monday_source_code, txt_backup_path)
        shutil.copyfile(monday_source_code, py_backup_path)
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
            monday_speak('My systems are off standby and fully active')
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
