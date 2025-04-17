from vosk import Model, KaldiRecognizer
import vosk_model
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import queue
import json


# engine and model variables + their associated variables
vosk_mod = Model('vosk_model')# name of the folder where vosk model is downloaded
kaldi_recognizer = KaldiRecognizer(vosk_mod, 16000)
queue = queue.Queue()
recogniser = sr.Recognizer() # speech recognition module shorthand
engine = pyttsx3.init() # text to speech engine

keyboard_input: bool = False # if True, take command from user via keyboard
online: bool = False # True for google speech recognition and False for vosk (google is more accurate but vosk is faster)
wake_up_word: str = "arise" # use this to wake assistant up
kill_word: str = "exit" # use this word to exit program (the voice input should only contain kill_word)


def speak(text: str) -> None:
    """
    Prints text, converts text to speech and speaks

    text: prints and speaks text
    """
    print(text)
    engine.say(text)
    engine.runAndWait()


def listen_wake_word() -> bool:
    """
    Listens for wake_word
    
    returns True if wake word is used
    """

    global online

    while True:
        word = take_command("Initialize by wake word...", 2, 2)
        
        if word is None: continue

        if wake_up_word in word:
            speak("At your command.")
            return True

        elif 'switch' in word:
            online = not online
            speak('Switch complete.')
            continue
                
        elif kill_word in word:
            speak('Purging Process.')
            exit()

        elif 'help' in word: speak(f'You can wake program by using "{wake_up_word}" or kill program by using "{kill_word}".')


def take_command(text: str = None, timeout: float = None, phrase_time_limit: float = None, wake:bool = False) -> str:
    if text is not None: print(text)
    
    while keyboard_input:
        try:
            command = input('Enter your command (switch to voice input by quit): ').strip().lower()

        except KeyboardInterrupt:
            print('KeyboardInterrupt.')
            continue

        if command == 'quit': speak('Quiting input command mode.')
        return command
        
    if online: return online_command(timeout, phrase_time_limit, wake)
    
    else: return offline_command(wake)


def online_command(timeout: float = None, phrase_time_limit: float = None, wake: bool = False) -> str | None:
    """
    Uses google API for speech recognition

    :param text: will print text before it starts to listen
    :param timeout: int to provide timeout to listen function
    :param phrase_time_limit: int to provide phrase_time_limit to listen function
    :param wake: bool to speak beep before listening
    :return: str after successfully recognizing or None
    """
    
    global online

    while online:
        try:
            with sr.Microphone() as source:
                print('Listening (Online)...')
                if wake:
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
            online = not online
            return

        except Exception as e:
            print(e)
            continue


def offline_command(wake: bool= False) -> str:
    """
    Uses vosk for offline speech recognition
    """

    def callback(indata, frames, time, status):
        if status: print(status, flush=True)
        
        queue.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
        print("Listening (Offline)...")
        if wake: speak('Beep')

        while True:
            data = queue.get()
            if kaldi_recognizer.AcceptWaveform(data):
                result = json.loads(kaldi_recognizer.Result())
                command = result.get("text", "").strip().lower()
                if command:
                    print(f"Vosk recognized: {command}")
                    return command

                else: print("No speech detected. Try again.")


if __name__ == '__main__':
    listen_wake_word()