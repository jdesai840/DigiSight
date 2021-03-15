import speech_recognition as sr
from gtts import gTTS
import time
from time import sleep
import random
import os
import pygame
from picamera import PiCamera
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials


r = sr.Recognizer()
pygame.mixer.init()
cog_key = '51aad77763794bd6a109a32167f646cb'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
classifier = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
sleep(1)


def mic_call2():
    with sr.Microphone() as source:
        print("Say something...")
        audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
        except sr.UnknownValueError:
            print('Sorry, I do not understand')
        except sr.RequestError:
            print('Sorry my speech service is down')
        return voice_data


def respond(voice_data):
    if 'scan' in voice_data:
        return 'Got it. What would you like to scan for?'
    if 'describe' in voice_data:
        description = describe_image()
        return description
    if 'exit' in voice_data:
        exit()
    
    
def speak(audio_text):
    tts = gTTS(text=audio_text, lang='en')
    r = random.randint(1, 2000000)
    audio_file = 'audio'+ str(r) + '.mp3'
    tts.save(audio_file)
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    os.remove(audio_file)


def describe_image():
    camera.capture('describe.jpg')
    image_path = ('describe.jpg')
    image_stream = open(image_path, 'rb')

    description = classifier.describe_image_in_stream(image_stream)

    for caption in description.captions:
        print(caption.text)
        confidence = caption.confidence * 100
        if confidence < 50:
            uncertainty_str = 'probably '
        elif confidence >= 50:
            uncertainty_str = ''
        
        spoken_text = uncertainty_str + caption.text
        return spoken_text
    
time.sleep(2)
print('How can I help you?')
while True:
    voice_data=mic_call2()
    response = respond(voice_data)
    print(response)
    try:
        speak(response)
    except AssertionError:
        print('No text to speak')

        

