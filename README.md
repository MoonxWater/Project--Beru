# Project Beru
This is a project I am doing while learning Python.
It takes command through microphone and wakes up after listening to the wake word within voice_input.py
You can also ask for "help" while it checks for wake word or you can simply close the program by the kill word within voice_input.py

### Input Choices:
1. Voice input (online) by google (online = True)
2. Voice input (offline) by vosk (current default) (online = False)
   (You can switch between these input mode by saying "switch")
3. Keyboard input (Enter "quit" to switch back to voice) (start by saying "input")

### Legal commands:
1. You can open websites and apps by saying "Open {website/app}". Some are already available in the code, or you can add their path in the dictionary within main.py
2. You can search on platform like YouTube, Google etc by saying "search {platform} {your_search}"
   (It can also search or open these if the first 3 letter are the same i.e "YouTube" and "You too" will be treated as "YouTube")
