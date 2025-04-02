import speech_recognition as sr
import webbrowser
import pyttsx3
import os, time
import pyautogui
# the four below modules help recognize audio input when google api fails or there is no internet connection
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json

# engine and model variables + their associated variables
recogniser = sr.Recognizer() # speech recognition module shorthand
engine = pyttsx3.init() # text to speech engine
vosk_model = Model('vosk-model-small-en-us-0.15')# name of the folder where vosk model is downloaded
kaldi_recognizer = KaldiRecognizer(vosk_model, 16000)
queue = queue.Queue()

# program needed global variables
online: bool = False
wake: bool = False # the assistant will not be wake at program initialization and you would need to use the wake up word and that will update wake to True
wake_up_word: str = "arise" # use this to wake assistant up
kill_word: str = "exit" # use this word to exit program (the voice input should only contain kill_word)
app_paths: dict = { "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
                    "epic games": "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
                    "code": os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
                    "brave": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
                    "opera": os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Opera GX Browser.lnk"),
                    } # if you want to add an app to be opened by the assistant, add its path to value and word to trigger opening in the key of app_paths dict
websites: dict = {'hi anime': 'https://hianime.is', # can be triggered in offline mode by saying hi amy or anything with "hi a"
                  'ashura': 'https://asuracomic.net/',# can be triggered in offline mode by saying ash
                  'reaper': 'https://reaperscans.com',
                  'youtube': 'https://youtube.com', # can be triggered in offline mode by saying you
                  'github': 'https://github.com/',
                  'google': 'https://google.com',
                  'chat gpt': 'https://chatgpt.com',
                  'geeks for geeks': 'https://www.geeksforgeeks.org/'
                  } # if you want to add a website to be opened by this program, add the url to value and trigger word in the key of websites dict


def speak(text: str) -> None:
    """
    Prints text, converts text to speech and speaks

    text: prints and speaks text
    """
    print(text)
    engine.say(text)
    engine.runAndWait()


def process_command(c: str) -> None:
    """
    Processes user voice commands

    :param c: command to be provided at function call
    :return: returns None
    """

    global wake, online

    if c.startswith('sleep'):
        # updates wake to False and returns to the point where it wakes after listening to wake word
        speak('Hibernating')
        wake = False
        return
    
    elif c.startswith(kill_word): # "c" should ideally contain only the kill_word and nothing else
        speak('Purging program.')
        exit()

    elif c.startswith('switch'):# switches between google(online) and vosk(offline) speech recog models
        online = not(online)
        speak('Switched mode.')
        return

    elif c.startswith('open'): # command to open
        c = c.replace('open', '', count=1).strip()
        opener(c)
        return
    
    elif c.startswith('search'): # command to search
        c = c.replace('search', '', count=1).strip()
        search(c)
        return


def opener(c: str):
    # to open websites
    if c in websites.keys():
        speak(f'Opening {c}')
        webbrowser.open(websites.get(c))

    # to open apps
    elif c in app_paths.keys():
        speak(f'Opening {c}')
        os.startfile(app_paths.get(c))

    else: # try to match initial words of the command with the available platforms in websites and app_paths
        speak(f'Cannot find a match for {c}. Trying pattern recognition.')
        c = platform_recognition_error(c)
        if c is False:
            return
        opener(c)
    return


def search(c: str):
    web_url = websites

    for platform, url in web_url.items():
        if c.startswith(platform):
            c = c.replace(f'{platform}', '', count=1).strip()
            no_error: bool = webbrowser.open(url)

            if no_error == False: 
                # if the open function in webbrowser module couldn't open url and returns False 
                speak(f'Something went wrong while opening {platform}')
                return
            
            time.sleep(2) # wait for url to open
            speak(f'Do you want to search {platform} for: {c}')
            confirmation = take_command("Confirm(yes/no)", 2, 2, wake)

            if ('okay' in confirmation) or ('ok' in confirmation) or ('yes' in confirmation):
                if f'{platform}' == 'youtube':
                    pyautogui.click(900, 140)

                speak(f"Searching for {c} on {platform}")
                pyautogui.typewrite(c, interval=0.1)
                pyautogui.press("enter")
                speak('Search Complete.')
                return
            
            elif 'no' in confirmation:
                speak("Cancelling search.")
                return
            
    speak(f'Cannot find a match for {c}. Trying pattern recognition.')
    c = platform_recognition_error(c)
    if c is False:
        return
    speak(f'What would you like to search on {c}?')
    search_query = c + take_command(f'What would you like to search on {c}?', 3, 3, wake)
    search(search_query)
            

def platform_recognition_error(c: str) -> str:
    web_url = websites
    app_dir = app_paths

    for platform in web_url.keys():
        if c[:3] == platform[:3]:
            speak(f'Did you mean {platform}?')
            return str(platform)
           
    for app in app_dir.keys():
        if c[:3] == app[:]:
            speak(f'Did you mean {app}?')
            return str(app)
        
    speak(f'No match') 
    return False   


def listen_wake_word():
    global wake, online

    while True:
        word = take_command("Initialize by wake word...", 2, 2, wake)
        
        if word is None:
            continue

        if wake_up_word in word:
            wake = True
            speak("At your command.")
            while wake == True:
                command = take_command("Jarvis Active...", 2, 3, wake)
                process_command(command)

        elif 'switch' in word:
            online = not(online)
            speak('Switched mode.')
            continue
                
        elif kill_word in word:
            speak('Purging Process.')
            exit()

        elif 'help' in word:
            speak(f'You can wake program by using "{wake_up_word}" or kill program by using "{kill_word}".')


def take_command(text: str, timeout: float = None, phrase_time_limit: float = None, wake:bool = wake) -> str:
    """
    :param text: will print text before it starts to listen
    :param timeout: int to provide timeout to listen function
    :param phrase_time_limit: int to provide phrase_time_limit to listen function
    :param wake: bool to speak beep before listening
    :return: str after successfully recognizing.
    """

    global online
        
    while online:
        try:
            print(text)
            with sr.Microphone() as source:
                print('Listening (Online)...')
                if wake == True:
                    speak('Beep')
                audio = recogniser.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print('Recognizing...\n')
            print(command := str(recogniser.recognize_google(audio)).lower().strip())
            return command

        except sr.UnknownValueError:
            print("Couldn't catch that...")
            continue

        except sr.RequestError:
            print('Speech Recognition API request failed. Switching to offline mode.')
            online = False
            break

        except Exception as e:
            print(e)
            continue

    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        queue.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
        print("Listening (Offline)...")
        if wake == True:
            speak('Beep')
        while True:
            data = queue.get()
            if kaldi_recognizer.AcceptWaveform(data):
                result = json.loads(kaldi_recognizer.Result())
                command = result.get("text", "").strip().lower()
                if command:
                    print(f"Vosk recognized: {command}")
                    return command

                else: print("No speech detected. Try again.")


def main():
    speak('Initializing')        

    listen_wake_word()


if __name__ == '__main__':
    main()