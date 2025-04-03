import webbrowser
import os, time
import pyautogui
import voice_input as vi

keyboard_input: bool = False # if True, take command from user via keyboard
wake: bool = False # the assistant will not be awake at program initialization, and you would need to use the wake_up word and that will update wake to True
app_paths: dict = { "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
                    "epic games": "C:\\Program Files (x86)\\Epic Games\\Launcher\\Portal\\Binaries\\Win32\\EpicGamesLauncher.exe",
                    "code": os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
                    "brave": os.path.expandvars("%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
                    "opera": os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Opera GX Browser.lnk"),
                    } # if you want to add an app to be opened by the assistant, add its path to value and word to trigger opening in the key of app_paths dict
websites: dict = {'hi anime': 'https://hianime.is/home', # can be triggered in offline mode by saying hi anny or anything with "hi a"
                  'youtube': 'https://youtube.com', # can be triggered in offline mode by saying you
                  'ashura': 'https://asuracomic.net/',# can be triggered in offline mode by saying ash
                  'google': 'https://google.com',
                  'chat gpt': 'https://chatgpt.com',
                  'reaper': 'https://reaperscans.com',
                  'github': 'https://github.com/',
                  'geeks for geeks': 'https://www.geeksforgeeks.org/'
                  } # if you want to add a website to be opened by this program, add the url to value and trigger word in the key of websites dict


def process_command(c: str) -> None:
    """
    Processes user voice commands

    :param c: command to be provided at function call
    :return: returns None
    """

    global wake, keyboard_input

    if c.startswith('sleep'):
        # updates wake to False and returns to the point where it wakes after listening to wake word
        vi.speak('Hibernating')
        wake = False
        return
    
    elif c.startswith(vi.kill_word): # "c" should ideally contain only the kill_word and nothing else
        vi.speak('Purging program.')
        exit()

    elif c.startswith('model switch'):# switches between google(online) and vosk(offline) speech recognition models
        vi.online = not vi.online
        vi.speak('Switch complete.')
        return
    
    elif c.startswith('input switch'):
        keyboard_input = not keyboard_input
        vi.speak('Switched Input mode.')
        command = vi.take_command('Waiting for input...', wake=wake)# timeout=0 and phrase_time_limit=0 means keyboard input
        process_command(command)
        return

    elif c.startswith('open'): # command to open
        c = c.replace('open', '', count=1).strip()
        opener(c)
        return
    
    elif c.startswith('search'): # command to search
        c = c.replace('search', '', count=1).strip()
        search(c)
        return
    
    elif c.startswith('type'):
        c = c.replace('type', '', count=1)
        vi.speak('Waiting for input...')
        type_value = vi.take_command('Waiting for input...', 3, 3, wake)
        vi.speak(f'Typing: {type_value}')
        pyautogui.typewrite(type_value, interval=0.1)


def opener(c: str):
    if c == ' ' or c == '': 
        print('Websites available:')
        [print(f'{x}. Open {w}') for x, w in enumerate(websites.keys())]
        print('Apps available:')
        [print(f'{i}. Open {a}') for i, a in enumerate(app_paths.keys())]
        return

    # to open websites
    if c in websites.keys():
        vi.speak(f'Opening {c}')
        webbrowser.open(websites.get(c))

    # to open apps
    elif c in app_paths.keys():
        vi.speak(f'Opening {c}')
        os.startfile(app_paths.get(c))

    else: # try to match initial words of the command with the available platforms in websites and app_paths
        vi.speak(f'Cannot find a match for {c}')
        c = platform_recognition_error_correction(c)
        if c is None: return
        opener(c)
        return


def search(c: str):
    web_url = websites
    if c == '' or c == ' ': 
        print('Websites available:')
        [print(f'{x}. Search {w} <--your_input_here-->') for x, w in enumerate(websites.keys())]
        print('Search is currently not available for github and geeks for geeks')
        return

    # looking for the platform
    for platform, url in web_url.items():
        if c.startswith(platform):
            c = c.replace(f'{platform}', '', count=1).strip()
            if platform != 'youtube':
                no_error: bool = webbrowser.open(url)
                if not no_error:
                    # if the open function in webbrowser module couldn't open url and returns False 
                    vi.speak(f'Something went wrong while opening {platform}')
                    return
            
            time.sleep(2) # wait for url to open
            vi.speak(f'Do you want to search {platform} for: {c}')
            confirmation = vi.take_command("Confirm(yes/no)", 2, 2, wake)

            if ('okay' in confirmation) or ('ok' in confirmation) or ('yes' in confirmation):
                if platform == 'youtube':
                    vi.speak(f"Searching for {c} on {platform}")
                    webbrowser.open(f'https://www.youtube.com/results?search_query={c}')
                    vi.speak('Search Complete.')
                    return
                
                elif platform == 'hi anime':
                    pyautogui.click(450, 140)

                elif platform == 'reaper':
                    pyautogui.click(1600, 150)

                vi.speak(f"Searching for {c} on {platform}")
                pyautogui.typewrite(c, interval=0.1)
                pyautogui.press("enter")
                vi.speak('Search Complete.')
                return
            
            elif 'no' in confirmation:
                vi.speak("Cancelling search.")
                return
            
    vi.speak(f'Cannot find a match for {c}.')
    c = platform_recognition_error_correction(c)
    if c is None: return

    vi.speak(f'What would you like to search on {c}?')
    search_query = c + vi.take_command(f'What would you like to search on {c}?', 3, 3, wake)
    search(search_query)
    return
            

def platform_recognition_error_correction(c: str) -> str | None:
    '''
    tries to find a match for the provided platform by matching the first 3 characters with the platforms in websites dict
    
    c: argument to be provided when it cannot be found within websites dict
    '''
    web_url = websites
    app_dir = app_paths

    for platform in web_url.keys():
        if c[:3] == platform[:3]:
            vi.speak(f'{platform} is a match.')
            return str(platform)
           
    for app in app_dir.keys():
        if c[:3] == app[:]:
            vi.speak(f'{app} is a match.')
            return str(app)
        
    vi.speak(f'No match') 
    return None   


def main():
    global wake

    vi.speak('Initializing') 

    while not wake:
        wake = vi.listen_wake_word()
        while wake:
            command = vi.take_command("Jarvis Active...", 2, 3, wake)
            process_command(command)


if __name__ == '__main__':
    main()