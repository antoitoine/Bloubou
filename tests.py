import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

for voice in voices:
    print(voice.id)
    engine.setProperty("rate", 178)
    voice.gender = "male"
    engine.setProperty("voice", voice.id)
    engine.say("Bonjour je m'appelle Antoine et je suis beau")
    engine.runAndWait()
    engine.stop()
