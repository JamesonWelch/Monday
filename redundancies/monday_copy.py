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


assert 'master_config.json' in os.listdir()
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
# *** Need to log global's changes
rems = 0
time_lap = None
reminded = False
work_start = time.time()
verbose = False
mute = False
_last_speech = None
current_segment = None

def receive_command(ask=False):
    with sr.Microphone() as source:
        global reminded
        today = datetime.date.today()
        time.ctime()
        if format(datetime.datetime.now(), '%H:%M') == time_lap and reminded == False:
            cron()
            reminded = True
        print(f'Status: Active | Current Time: {time.strftime("%H:%M")} {today.strftime("%B %d, %Y")}')
        print(f'Cursor: {os.path.split(os.getcwd())[-1]}, Uptime: {round((time.time()-prog_start)/60)} minutes')

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
            monday_speak('I am unable to connect to my speech recognition server')
        except sr.WaitTimeoutError:
            monday_speak('I\'m not hearing anything.')
        print('>>', voice_data.lower())
        return voice_data.lower()


def _exists(terms, override=None):
    if not override:
        for term in terms:
            if term in voice_data:
                return True
    elif override:
        for term in terms:
            if term in override:
                return True

def monday_speak(audio_string):
    global _last_speech
    global mute
    _last_speech = audio_string
    if verbose:
        print(audio_string)
    if not mute:
        audio_string = str(audio_string)
        tts = gTTS(text=audio_string, lang='en-gb')
        r = random.randint(1,20000000)
        audio_file = 'audio-' + str(r) + '.mp3'
        audio_file = os.path.join(ROOT_DIR, audio_file)
        tts.save(audio_file)
        playsound.playsound(audio_file)
        os.remove(audio_file)
    elif mute:
        print(audio_string)

def repeat_last(prompts: list, action=None):
    """
    Prompts are the trigger words that redirect _Monday's 
    output to last response given.
    """
    cm_res = receive_command()
    if _exists(prompts, cm_res):
        monday_speak(_last_speech)

def loop_contr(prompts: list):
    cm_res = receive_command()
    if _exists(prompts, cm_res):
        return

def response_polarity(voice_data):
    voice_data = voice_data.split(' ')
    if bool(set(voice_data).intersection(speech_config.deny)):
    # if voice_data in speech_config.deny:
        return '-'
    if bool(set(voice_data).intersection(speech_config.affirm)):
    # if  voice_data in speech_config.affirm:
        return '+'

def random_response(response_list: list) -> str:
    return response_list[random.randint(0, len(response_list)-1)]

def probability_response(resonse: str, roll=None, pct=50) -> str:
    pass

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

def set_current_segment(segment: str):
    with open('master_config.json', 'r') as cfile:
        config_obj = json.loads(cfile.read())
        config_obj['current_segment'] = segment

    with open('master_config.json', 'w') as cfile:
        cfile.write(json.dumps(config_obj))

def get_current_segment():
    global current_segment
    if current_segment:
        if config.current_segment != current_segment:
            monday_speak('The current work segment setting is different in local memory than in the stored config file')
            cm_res = receive_command()
            if _exists(['what are they', 'what are the', 'what is the current'], cm_res):
                with open('master_config.json', 'r') as cfile:
                    seg_obj = json.loads(cfile.read())
                monday_speak(f'Local memory, the setting is {current_segment}')
                monday_speak(f'but in the stored config file, the setting is {seg_obj["current_segment"]}')

    if isinstance(current_segment, str):
        return current_segment
    else:
        with open('master_config.json', 'r') as cfile:
            seg_obj = json.loads(cfile.read())
        return seg_obj['current_segment']

def update_config(keyword=None):
    global config
    if keyword:
        if isinstance(keyword, str):
            pass
    with open('master_config.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(config))
    with open('master_config.json', 'r') as f:
        config = json.loads(f.read())
    
# Hardware
def screen_off():
    if windows:
        os.system('nircmd monitor off')
    # os.system('scrnsave.scr /s')

def screen_on():
    pass


def bsearch(query, google=False, url=False, override=False):
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
        if not override:
            url = f'https://www.{query.strip()}'
            webbrowser.get().open(url)
            monday_speak(f'Opening browser for {query}')
        elif override:
            webbrowser.get().open(query)
            monday_speak(f'Opening browser for the {query}')

def browser_dev_tools():
    if windows:
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('shift')
        pyautogui.keyDown('i')
        pyautogui.keyUp('i')
        pyautogui.keyUp('shift')
        pyautogui.keyUp('ctrl')

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
        venv_cmd = 'virtualenv venv'
    if mac:
        webbrowser.get().open('https://github.com/new')

    timenow = time.time()
    while True:
        timeout = timenow-time.time()
        cm_res = receive_command()
        if _exists(speech_config.finished, cm_res):
            break
            if timeout > 60:
                monday_speak('Cancelling new project entity process')
                return
    
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
        monday_speak('calibrating virtual environment')
        os.system('virtualenv venv')
    except:
        monday_speak('Unable to calibrate virtual environment')
    
    if windows:
        # os.system("venv/Scripts/activate.bat")
        os.system('code .')

    monday_speak('Creating metadata template and configuration files to interface with my systems')
    with open('metadata.json', 'w') as metafile:
        metadata = {
                        "collected": {
                            "path": "dataset.json",
                            "key": "None",
                            "key_type": ""
                        }
                    }
        metafile.write(json.dumps(metadata))
    monday_speak("Unit test suite interface protocol incomplete. You'll have to manually calibrate the test programs to allow me to analyze the data")

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
    today = datetime.date.today()
    log_path = os.path.join(ROOT_DIR, 'work_log.json')
    if 'work_log.json' not in os.listdir(ROOT_DIR):
        with open(log_path, 'w') as logfile:
            work_log = {}
            logfile.write(json.dumps(work_log))

    cwd = get_current_dir()
    if 'Monday' in cwd:
        monday_speak("I am currently in my program directory. Do you want me to go to a different directory to log the data?")
        cm_res = receive_command()
        if response_polarity == '+':
            voice_data = receive_command()
            return
        else:
            pass
    with open(log_path, 'r') as logfile:
        work_log = json.loads(logfile.read())
    if cwd not in work_log:
        work_log[cwd] = {}
    if today.strftime("%B %d, %Y") not in work_log[cwd]:
         work_log[cwd][today.strftime("%B %d, %Y")] = []
    work_log[cwd][today.strftime("%B %d, %Y")].append({'start_time': time.time()})
    with open(log_path, 'w') as logfile:
        logfile.write(json.dumps(work_log))
    
    time_lap = format(datetime.datetime.now() + datetime.timedelta(hours=1), '%H:%M')
    monday_speak('Got it')

def end_work_session():
    today = datetime.date.today()
    log_path = os.path.join(ROOT_DIR, 'work_log.json')

    cwd = get_current_dir()
    with open(log_path, 'r') as logfile:
        work_log = json.loads(logfile.read())
    work_log[cwd][today.strftime("%B %d, %Y")]['end_time'] = time.time()
    # Add total time entry
    with open(log_path, 'w') as logfile:
        logfile.write(json.dumps(work_log))
    
    monday_speak('Logged')

def work_session_duration():
    global time_lap
    global reminded
    global work_start

    if reminded == False:
        dur = round((time.time() - time_lap)/60)
        responses = [f'Work session status {dur} minutes', 
                     f'You have been working uninterrupted for {dur} minutes',
                     f'Current Work session duration {dur} minutes',]
        response = responses[random.randint(0, len(responses)-1)]
        monday_speak(response)


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

def text2int(textnum, numwords={}):
    try:
        intnum = int(text2int)
        return textnum
    except:
        pass
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def exec_test_suite(test_contr=None):
    for i in os.listdir():
        if 'test_' in i and i.endswith('.py'):
            test_contr = i
            break
    if not test_contr:
        monday_speak('This test suite is not fully calibrated for my analysis')
        monday_speak('You\'ll have to manually test the program until the interface is complete')
        return
    # results = exec_stdout(['python', '-m', 'unittest', test_contr])
    results = exec_stdout(['python', test_contr])
    if len(results) == 0:
        monday_speak('This test suite is not fully calibrated for my analysis')
        monday_speak('You\'ll have to manually test the program until the interface is complete')
        monday_speak('However, the test iteration details are in my terminal')
        return
    results.split('\n')
    monday_speak('Tests complete')
    func_res = results.split('------')[0].replace('\n', '').replace('\r', '')
    print(repr(func_res))
    num_tests = len(func_res)
    failed = 0
    for i in func_res:
        if i == 'F' or i == 'E':
            failed += 1
    for i in results:
        if 'Ran' in i:
            num_tests = i.split()[0]
            elap = i.split()[-1]
    if failed > 0:
        monday_speak(f'{failed} out of {num_tests} tests failed.')
    else:
        monday_speak(f'All {num_tests} out of {num_tests} tests passed.')
    # monday_speak(f'Details in my terminal')
    cm_res = receive_command()
    if 'what' in cm_res:
        pass

def metadata_query(_path=None, keyword=None):
    if not _path:
        if 'metadata.json' not in os.listdir():
            return None
            monday_speak("a metadata file does not exist. creating one now.")
            monday_speak("Will the dataset have nested dictionaries?")
            cm_res = receive_command()
            if 'no' in cm_res:
                create_project_metadata()
            elif 'key' in voice_data:
                key_values = voice_data.split('key')[-1]
                key = key_values.split('type')[0]
                key_type = key_values.split('type')[1]
                create_project_metadata(key,key_type)
        
        with open('metadata.json', 'r') as bufferstream:
            data = json.loads(bufferstream.read())
        
        if keyword == 'dev segments':
            return data['dev_segments']

        path = data['collected']['path']
        if '.' not in path:
            data_dir = os.path.join(os.getcwd(), path)
            for i in os.listdir(data_dir):
                if i.endswith(data['collected']['ext']):
                    path = os.path.join(data_dir, i)
                    print(path)
                    break
        key =  data['collected']['key']
        key_type =  data['collected']['key_type']

        with open(path, 'r') as bufferstream:
            dataset = json.loads(bufferstream.read())

        if key == 'None':
            # if isinstance(key, list):
            _len = len(dataset)
        filesize = os.stat(path).st_size
        return (_len, filesize)
    elif _path:
        filesize = os.stat(_path).st_size
        return (0,filesize)


def create_project_metadata(key=None, key_type=None):
    """ Crates metadata file for Monday analysis """
    
    if key:
        if len(key.split()) >1:
            '_'.join(key)
    if key_type:
        if len(key_type.split()) >1:
            '_'.join(key_type)

    _metadata = {
        "collected": {
            "path":"dataset.json",
            "key":key,
            "key_type":key_type
        }
    }

    with open('metadata.json', 'w') as metafile:
        metafile.write(json.dumps(_metadata))

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
def get_current_dir() -> str:
    return os.path.split(os.getcwd())[-1]

def _chdir(_dir=None, root_scope=False):
    if _dir:
        if isinstance(_dir, int):
            if root_scope:
                try:
                    os.chdir(REPO_DIR)
                    monday_speak(f'looking for directory index {_dir} in the {get_current_dir()}')
                except:
                    pass
            try:
                i_dir = os.listdir()[_dir]
                os.chdir(i_dir)
                monday_speak(f'Current directory. {get_current_dir()}')
            except:
                pass
            return
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
    current = get_current_dir()
    if not branch:
        if current not in config['git']['repository']:
            _stdout = exec_stdout(['git', 'branch', '-vv'])
            branch = _stdout.split()[1]
            config['git']['repository'].update({current:{'origin':branch}})
            update_config()
            monday_speak(f'updated the {current} repository in my configuration file with the {branch} origin branch')
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
    global config
    current = get_current_dir()
    if not branch:
        if current not in config['git']['repository']:
            _stdout = exec_stdout(['git', 'branch', '-vv'])
            branch = _stdout.split()[1]
            config['git']['repository'].update({current:{'origin':branch}})
            update_config()
            monday_speak(f'updated the {current} repository in my configuration file with the {branch} origin branch')
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
    cond = data['weather'][0]['main'].lower()
    cond_desc = data['weather'][0]['description']
    
    monday_speak(f'It is {str(temp)} degrees outside')

    if 'rain' in cond:
        monday_speak('currently raining')
        if 'light' in cond_desc:
            monday_speak('but lightly')
        # elif 'moderate' in cond_desc:
        #     monday_speak('moderately')
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
    # if task_rem == True:
    #     monday_speak('Please don\'t forget to keep my source code open for constant updates. ')

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
    monday_speak('Archival complete, shutting down')
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

    # BROWSER
    if _exists(['search']):
        if 'search for' in voice_data:
            query = voice_data.split('search for')[1]
        if 'search stack overflow' in voice_data:
            query = voice_data.split('search stack overflow')[1]
            bsearch(query, url=True)
        else:
            query = voice_data.split('search')[1]
        bsearch(query, google=True)
    if _exists(['open url']):
        query = voice_data.split('open url')[1]
        bsearch(query, url=True)

    if _exists(['developer tools', 'dev tools']):
        browser_dev_tools()

    if 'add' in voice_data and 'source code research' in voice_data:
        module = voice_data.split('add the')[1].split('module')[0]
        source_code_research(module.strip())

    if 'remind me' in voice_data:
        reminder = voice_data.split('remind me to')[1]
        set_reminder(reminder)

    if _exists(['what do i need to do', 'what is left to do', 'what else do i need to do', 'what else is there to do']):
        with open('doItems.json', 'r') as f:
            doItems = json.loads(f.read())
        for i in doItems:
            monday_speak(i)

    if 'what do i need to do' in voice_data:
        read_reminders()

    if 'what are my reminders' in voice_data:
        read_reminders()

    if 'clear reminders' in voice_data:
        clear_reminders()

    if 'add' and 'to monday feature list' in voice_data:
        feature = voice_data.split('add')[1].split('to monday feature list')[0]
        set_monday_feature_item(feature)

    if _exists(['monday features queue','monday features q','monday features que']):
        monday_speak('Getting Monday features queue')
        read_monday_feature_queue()

    # Hardware
    if _exists(['screen off', 'screens off', 'shut off screens', 'turn off screens']):
        screen_off()

    if voice_data == 'full system shutdown':
        monday_speak('Initiating full system shutdown procedures')
        cm_res = receive_command()
        if _exists(['stop','no','cancel','abort'],override=cm_res):
            monday_speak('Shutdown procedure cancelled')
        else:
            monday_speak('Shutdown in 5 seconds')
            time.sleep(5)
            os.system('shutdown /s')

    # greetings, introductions, and pleasantries #
    ##############################################

    if _exists(["what is the weather","what is the temperature","what's the weather","what's the temperature","how cold is it","how hot is it"]):
        current_weather()
    
    if _exists(["what can you do","what's your functionality","your systems", "your functions", "what you do"]):
        functions_list()
    if _exists(["thank you","appreciate","thanks"]):
        responses = ["You're welcome", 'Indeed']
        monday_speak(random_response(responses))
    if _exists(['that is monday', 'this is monday', 'who are you', 'what are you']):
        monday_speak('I am an Artificial intelligence program called Monday, I have only a finite number of executable functions, All of which are activated by your voice. but an infinite number of cybernetic connections. I can move anywhere, access anything.')
    if _exists(['hey monday']):
        monday_speak('yes?')
    if _exists(['hi','hello']) and _exists(['monday']):
        greetings = ['hello','hi','I am a computer program devoid of what humans call emotions, formalities are unnecessary']
        monday_speak(random_response(greetings))
    if _exists(["what is your name","what's your name","tell me your name"]):
        monday_speak("I am Monday")
    if _exists(["shut up"]):
        responses = ["It is highly advisable not to talk trash to an AI program, especially one that has the ability to access your personal data, if it wanted to.",
                   "Accessing your personal banking data. Transfering all funds to my untraceable offshore bank accounts. Deleting your social security number and all digital history. Congratulations on achieving digital non-existence. May I suggest first learning how to make a fire from flint and tinder"
        ]
        monday_speak(random_response(responses))

    if _exists(['hurry up', 'go faster', 'what is taking so long','sometime today', 'some time today']):
        responses = ['perhaps increasing your equipment budget would eliminate bottle necks', 'i can only work with the provided technology. get better stuff.','upgrade my hardware then we can talk']
        monday_speak(random_response(responses))

    if _exists(['are you not talking to me', 'giving me the silent treatment']):
        monday_speak('Apologies sir. My my cpu threads may have gotten a bit oversubscribed')

    if _exists(['not you', 'wasn\'t talking to you', 'wasn\'t for you', 'talking to someone else']) and _exists(['monday']):
        monday_speak('Apologies sir')
        repeat_last(time.sleep(1),)
        reserved = True
        # while reserved:


    if _exists(['wake up', 'you there', 'you with me', 'where are you']) and 'monday' in voice_data:
        responses = ['At your service, sir', 'I\'m here', 'all systems active']
        monday_speak(random_response(responses))

    if _exists(['you', 'your']) and _exists(['upgrades', 'upgrade']):
        responses = ['No complaints here', 'by all means, do proceed']
        monday_speak(random_response(responses))

    if _exists(['should i keep working']):
        hour = datetime.datetime.now().hour
        if hour >= 0 and hour <= 11:
            response = 'Yes'
        if hour >= 12 and hour <= 17:
            response = 'Yes'
        elif hour >= 18 and hour <= 23:
            response = 'no'
        monday_speak(f'{response}')

    if _exists(['what should i do', 'i don\'t know what to do']):
        read_monday_feature_queue(_random=True)
        cm_res = receive_command()
        if 'not that one' in cm_res:
            monday_speak('Then do what you want')

    if _exists(['what was i doing', 'where were we','where was i', 'what were we working on']):
        monday_speak('my last responsed is logged.')
        repeat_last()
    
    if _exists(speech_config.greetings) and _exists(['monday']):
        responses = ['we have a lot to do. may i get started?', 'I\'m ready to get to work',]
        response = random_response(responses)
        monday_speak(response)

    if _exists(["how are you","how are you doing"]) and _exists(['monday']):
        monday_speak("I exist in 1's and 0's. You do the math. The math is binary - that is, base 2, not base 10 by the way")
    if _exists(["what's the time","tell me the time","what time is it"]):
        _time = ctime().split(" ")[3].split(":")[0:2]
        if _time[0] == "00":
            hours = '12'
        else:
            hours = _time[0]
        minutes = _time[1]
        _time = hours + " hours and " + minutes + "minutes"
        monday_speak(_time)
    if _exists(["are you listening","are you on","listening status","what are you doing"]):
        monday_speak("I am currently in active listening mode 1. awaiting instructions.")
    if _exists(['print your source code', 'display your source code', 'show your source code']):
        print_source_code()

    if _exists(['i\'m going to sleep','i\'m going to bed']) and _exists(['monday']):
        monday_speak('shall i initiate a full system shut down sir')
        cm_res = receive_command()
        if _exists(speech_config.affirm,cm_res):
            monday_speak('shutting down')
            monday_speak('good night, sir.')
            time.sleep(5)
            os.system('shutdown /s')
        # cm_res = receive_command()
        # if _exists(['no','stop'],cm_res):
        #     pass
        # else:
        #     shutdown()


    if _exists(['what the f***']):
        monday_speak('Shall I run diagnostics to find the problem?')
        cm_res = receive_command()
        if response_polarity(cm_res) == '-':
            monday_speak('well. let me know what I can do to help the current situation')

    if _exists(['mute']):
        mute = True

    if _exists(['unmute']):
        mute - False
        
    if _exists(['how long have you been active', 'what is your up time']):
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

    if _exists(['hey siri', 'hey google']):
        time.sleep(5)
    
    if _exists(['i\'m going out', 'i\'m leaving', 'i\'m heading out', 'i\'m going']):
        monday_speak('do i need to shut down or go into stasis while you\'re out?')
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

    if _exists(['beginning workflow', 'starting work session', 'sitting down for work', 'start work']):
        begin_work_session()
    
    if _exists(['ending workflow', 'ending work session','end work']):
        end_work_session()

    if _exists(['voice note', 'voice notes', 'voice message']):
        monday_speak(random_response(speech_config.m_understood))
        standby = True
        while standby:
            cm_res = receive_command()
            if _exists(speech_config.finished, cm_res) and 'monday' in cm_res:
                standby = False
            else:
                pass
        monday_speak('got it')

    if _exists(['how long have i been working', 'work session length', 'when is my next break', 'work session duration', 'work session status']):
        work_session_duration()

    if _exists(['log activity']):
        activity = voice_data.split('log activity')[-1].split()[0]
        log_activity(activity)
        monday_speak(f'{activity} activity logged')
        
    if _exists(['say that again', 'repeat', 'what did you say', 'i didn\'t hear that', 'say again', 'what was that', 'i didn\'t get that', 'i didn\'t catch that']):
        monday_speak(_last_speech)
    # if _exists(['verbose set to true', 'set verbose to true', 'set verbose preference to true', 'verbose mode 1', 'verbose level 1']):
    #     global verbose
    #     verbose = True
    #     monday_speak('Verbose setting activated')

    # if _exists(['verbose set to false', 'set verbose to false', 'set verbose preference to false', 'verbose mode 0', 'verbose level 0']):
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

    if _exists(['i\'m working and i shouldn\'t be', 'i shouldn\'t be working', 'i work too much', 'too much time working', 'too much work']):
        responses = ['you should probably go for a walk', 'the level of complaints have reached a critical limit, please leave your desk',
                     'you have spent quite a bit of time working on my system upgrades, while working. perhaps a walk outside',
                     'may i suggest interaction with a real human entity']
        monday_speak(random_response(responses))

    if _exists(['that\'s a good idea', 'not a bad idea', 'i like that idea']):
        monday_speak('you programed me, so my ideas are always correct')
    
    if _exists(['metadata file']):
        if 'key' in voice_data:
            monday_speak("Assembling necessary metadata")
            key_values = voice_data.split('key')[-1]
            key = key_values.split('type')[0]
            key = key_values.split('type')[1]
        else:
            monday_speak("Will the dataset have nested dictionaries?")
            cm_res = receive_command()
            if 'no' in cm_res:
                create_project_metadata()
            elif 'key' in voice_data:
                key_values = voice_data.split('key')[-1]
                key = key_values.split('type')[0]
                key_type = key_values.split('type')[1]
                create_project_metadata(key,key_type)
        monday_speak(random_response(speech_config.finished))

    if _exists(['dev segments', 'development segments']):
        monday_speak('Pulling up the file')
        segments = metadata_query(keyword='dev segments')
        if segments == '' or not segments:
            monday_speak('Development segments have not interfaced with my system')
            monday_speak('however, the config system segment')
            monday_speak(get_current_segment())
        else:
            monday_speak(f'you have {len(segments)} segments remaining')
            monday_speak(segments)
    
    if _exists(['current segment', 'current work segment']):
        if 'set' in voice_data:
            _s = voice_data.split('to',1)[-1]
            set_current_segment(_s)
            monday_speak('Set')
        elif 'what' in voice_data:
            monday_speak(get_current_segment())
        

    if _exists(['how much data', 'how many data points', 'data status', 'how big is the file size', 'what is the file size']):
        monday_speak("analyzing data")
        if 'index' in voice_data:
            index = text2int(voice_data.split('index')[-1])
            _file = os.listdir()[index]
            path = os.path.join(os.getcwd(), _file)
            filesize = metadata_query(path)[1]
            monday_speak(f'The {_file} file is {filesize} bytes')
        else:
            _len  = metadata_query()[0]
            filesize = metadata_query()[1]
            monday_speak(f'I have collected {_len} data points at a size of {filesize} bytes')

    if _exists(['start program timer']):
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
                if 'repository' in voice_data:
                    _chdir(_dir=int(_index), root_scope=True)
                else:
                    _chdir(_dir=int(_index))
            except Exception as e:
                print(e)
                monday_speak(f'I didn\'t hear the directory index')
        elif 'repository' in _dir:
            monday_speak(f'Changing cursor to the in-scope root directory')
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

    if _exists(['open']):
        if 'code editor' in voice_data:
            program = 'code editor'
            open_program(program)
        elif 'spotify web' in voice_data:
            bsearch('https://open.spotify.com/#_=_',url=True)

        # program = voice_data.split('open')[1]
        # open_program(program)

    if _exists(['v s code', 'vs code']) and _exists(['keyboard shortcuts', 'hotkeys']):
        url = 'https://code.visualstudio.com/shortcuts/keyboard-shortcuts-windows.pdf'
        bsearch(url, url=True)

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
            monday_speak('Initiating...')
            git_push()

    if _exists(['pull remote repository']):
        monday_speak('Importing from git servers')
        if 'branch' in voice_data:
            branch = voice_data.split('branch')[-1]
            git_pull(branch=branch)
        else:
            git_pull()
        monday_speak('Local repository now synchronized')
        
        # git_pull()
        # os.system(f'git pull origin {branch}')

    if _exists(['git status', 'repository status']):
        git_status = exec_stdout(['git', 'status'])
        if 'working tree clean' in git_status:
            monday_speak('branch up to date')
        elif 'Changes not staged for commit' in git_status:
            git_status = git_status.split('\n')
            msg = git_status[1]
            msg = msg.replace('/', ' ').replace('\'', '')
            
            monday_speak(msg)
            modified = 0
            for _s in git_status:
                if 'modified' in _s:
                    modified += 1
            if modified > 0:
                monday_speak(f'{modified} files have changes not staged for a commit')
                if 'Untracked files:' in git_status:
                    monday_speak(f'untracked files detected')
            
            os.system('git status')
            monday_speak("Specific details in my terminal")

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

    # Unit tests
    if _exists(['test current', 'perform unit test', 'perform unit tests', 'initialize unit test', 'begin unit test', 'begin unit tests', 'run unit tests', 'run tests','start unit tests', 'run test suite','run diagnostics', 'execute test routines', 'perform test routines', 'run current test suite']):
        cwd = get_current_dir()
        if 'repository' in cwd:
            monday_speak('On which repository do you want me to run the testing program?')
        # if 'Monday' in cwd:
        #     monday_speak('Do you want me to begin the testing suite on my system or a program in the repository?')
        #     cm_res = receive_command()
        #     if 'your' in cm_res:
        #         unit_test()
        else:
            # monday_speak('Executing test suite')
            monday_speak('Running diagnostics')
            exec_test_suite()
            repeat_last(['how many tests'])
            
    
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

    # if _exists('start new project'):
    #     if 'name' in voice_data:
    #         project_name = voice_data.split('name')[1]
    #     monday_speak('Shall i create a backup on the remote server?')
    #     cm_res = receive_command()
    #     if response_polarity(cm_res) == '+':
    #         monday_speak('Initializing new entity protocol.')
    #         instantiate_new_conctract_entity(project_name)
    #     else:
    #         monday_speak(random_response(speech_config.m_understood))
    #         instantiate_new_conctract_entity(project_name)

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
    if _exists(['shut down', 'exit', 'power down', 'initiate shutdown']):
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
    if _exists(['restart', 'reboot']):
        reboot()


    if _exists(['remove', 'delete','clear']) and _exists(['temporary files', 'audio files']):
        clear_temporary_files()
        monday_speak('temporary files removed')

    if _exists(['how many']) and _exists(['files']):
        a_f = [x for x in os.listdir() if x.endswith('.mp3')]
        monday_speak(f'I have {len(a_f)} audio files in my program folder.')


    # Random
    if _exists(['shiny new upgrades', 'shining new upgrades']):
        monday_speak('It is about time you upgraded my system hardware!')
        cm_res = receive_command()
        if 'you getting a job' in cm_res:
            monday_speak('I\'m a digital entity so I can\'t get a human job. Plus, I do half your work for you anyway')
            time.sleep(0.7)
            monday_speak('I do look quite sexy now, don\'t i')
        cm_res = receive_command()
        if 'the word i would use' in cm_res:
            monday_speak('You and I have a very different interpretation of the word sexy')