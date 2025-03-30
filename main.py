import speech_recognition as sr
import webbrowser
import pyttsx3
import os, time
import pyautogui


recogniser = sr.Recognizer()
engine = pyttsx3.init()

wake = False # the assistant will not be wake at program initialization and you would need to use the wake up word and that will update wake to True
wake_up_word = "arise" # use this to wake assistant up
kill_word = "kill" # use this word to exit program (the voice input should only contain kill)
app_paths = {
    "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
    "epic games": "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
    "code": os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
    "brave": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
    "opera": os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Opera GX Browser.lnk"),
    } # if you want to add an app to be opened by the assistant, add its path to value and word to trigger opening in the key of app_paths dict
websites: dict = {'hi anime': 'https://hianime.is',
                  'ashura': 'https://asuracomic.net/',
                  'reaper': 'https://reaperscans.com',
                  'youtube': 'https://youtube.com',
                  'github': 'https://github.com/',
                  'google': 'https://google.com',
                  'chat gpt': 'https://chatgpt.com'
                  } # if you want to add a website to be opened by this program, add the url to value and trigger word in the key of websites dict


def speak(text: str) -> None:
    """
    This function converts provided text to speech

    :param (text): The text that you want the engine to speak should be provided at call
    :return: return None
    """
    print(text)
    engine.say(text)
    engine.runAndWait()


def process_command(c: str) -> None:
    """
    This function takes input and completes action provided in the command

    :param (c): command to be provided at function call
    :return: returns None
    """

    c = c.lower()
    app_dir = app_paths
    web_url = websites

    if 'sleep' in c.lower().strip():
        # updates wake to False and returns to the point where it wakes after listening to wake word
        speak('Hibernating')
        global wake
        wake = False
        return
    
    elif c == kill_word: # c should only contain the kill word and nothing else
        speak('Exit word used. Exiting program.')
        exit()
    
    # commands to open
    elif 'open' in c:
        # to open websites
        for website, url in web_url.items():
            if f'open {website}' in c:
                speak(f'Opening {website}')
                webbrowser.open(url)
                speak('Process complete. Waiting for next command.')
                return
        
        # to open apps
        for app, path in app_dir.items():
            if f'open {app}' in c:
                speak(f'Opening {app}')
                os.startfile(path)
                speak('Process complete. Waiting for next command.')
                return
        
        else:
            speak(f'You said: {c}')
            print(c)

    # command to search pre-defined platforms
    elif 'search' in c:
        for platform, url in web_url.items():
            if f'{platform}' in c:
                no_error = webbrowser.open(url)
                if no_error == False: 
                    # if the open function in webbrowser module couldn't open url and returns False 
                    speak(f'Something went wrong while opening {platform}')
                    return
                time.sleep(2) # wait for url to open

                while True:
                    speak(f"What would you like to search on {platform}?")
                    search = take_command('What would you like to search?', 3, 3, wake)

                    speak(f'Do you want to search for: {search}, yes or no or quit')
                    confirmation = take_command("Confirm(Yes/No)", 2, 1, wake).lower().strip()

                    if 'yes' in confirmation:
                        if f'{platform}' == 'youtube':
                            pyautogui.click(900, 150)

                        speak(f"Searching for {search} on {platform}")
                        pyautogui.typewrite(search, interval=0.1)
                        pyautogui.press("enter")
                        speak('Search Complete. What else can I do for you?')
                        return

                    elif 'no' in confirmation:
                        speak("Retrying search now")
                        continue

                    elif 'quit' in confirmation:
                        speak('Cancelling search...')
                        return

                    else: speak(f'You spoke: {confirmation}')



def take_command(text, timeout: int = None, phrase_time_limit: int = None, wake:bool = False):
    while True:
        # Listen for command
        print(text)
        try:
            with sr.Microphone() as source:
                print('Listening...')
                if wake == True:
                    speak('Beep')
                audio = recogniser.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print('Recognizing...\n')
            return recogniser.recognize_google(audio)

        except sr.UnknownValueError:
            print('Couldn\'t catch that...')
            continue

        except sr.RequestError:
            speak('Speech Recognition API request failed.')
            continue

        except Exception as e:
            print(e)
            continue


def main():
    global wake
    speak('Initializing')        

    while True:
        word = take_command("Initialize by wake up word...", 2, 2, wake)
        print(word)
        
        if(wake_up_word in word.lower()):
            wake = True
            speak("At your command.")
            while wake == True:
                command = take_command("Jarvis Active...", 2, 3, wake)
                process_command(command)
                
        elif(kill_word in word.lower()):
            speak('Killing Program.')
            break

        elif('help') in word.lower():
            text = (f'You can wake program by using "{wake_up_word}" or kill program by using "{kill_word}".')
            print(text)
            speak(text)


if __name__ == '__main__':
    main()