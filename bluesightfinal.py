import os
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from PIL import Image
import asyncio
from bleak import BleakClient
from bleak import discover
from neosensory_python import NeoDevice
import speech_recognition as sr
from gtts import gTTS
import time
import random
import pygame
from picamera import PiCamera
from time import sleep


endpoint = "https://hackathonformrecog.cognitiveservices.azure.com/"
key = "10313789480245228ba917ab386fef94"
cog_key = '51aad77763794bd6a109a32167f646cb'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
classifier = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

r = sr.Recognizer()
pygame.mixer.init()

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


def directional_guidance():
    camera.capture('guidance.jpg')
    image_path = ('guidance.jpg')
    image_stream = open(image_path, 'rb')
    image = Image.open('street.jpg')
    width, height = image.size
    features = ['Description', 'Objects', 'Categories']
    description = classifier.analyze_image_in_stream(image_stream, visual_features = features)
    
    if description.objects:
        name_array = []
        obj_distance_array = []
        position_array = []
        for object in description.objects:
            r = object.rectangle
            obj_area = (r.w * r.h)
            img_area = width * height
            obj_distance = obj_area/img_area
            x_coord = (r.x + (r.w)/2)
            name = object.object_property
            position = x_coord/width
            name_array.append(name)
            obj_distance_array.append(obj_distance)
            position_array.append(position)
        os.remove('guidance.jpg')
        return name_array, obj_distance_array, position_array


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


async def run(loop):
    #Establishing a bluetooth connection to the Neosensory Buzz
    buzz_addr = "EB:D0:EA:CD:7E:4E"
    devices = await discover()
    for d in devices:
        if str(d).find("Buzz") > 0:
            print("Found a Buzz! " + str(d) +
             "\r\nAddress substring: " + str(d)[:17])
            buzz_addr = str(d)[:17]


    async with BleakClient(buzz_addr, loop=loop) as client:
        my_buzz = NeoDevice(client)
        await asyncio.sleep(1)
        x = await client.is_connected()
        print("Connection State: {0}\r\n".format(x))
#       await my_buzz.enable_notifications(notification_handler)
        await asyncio.sleep(1)
        await my_buzz.request_developer_authorization()
        await my_buzz.accept_developer_api_terms()
        await my_buzz.pause_device_algorithm()
        
        motors_pause = [0, 0, 0, 0]
        
        qdelay = 0.08


        async def obj_not_found():
            await my_buzz.vibrate_motors([255, 255, 255, 255])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([255, 255, 255, 255])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)


        async def pattern_left(intensity):
            print("Vibrational intensity: " +  str(intensity))
            await my_buzz.vibrate_motors([intensity, 0, 0, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([0, intensity, 0, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([0, 0, intensity, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([0, 0, 0, intensity])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
        
        
        async def pattern_right(intensity):
            print("Vibrational intensity: " +  str(intensity))
            await my_buzz.vibrate_motors([0, 0, 0, intensity])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([0, 0, intensity, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([0, intensity, 0, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
            await my_buzz.vibrate_motors([intensity, 0, 0, 0])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
        
        
        async def pattern_straight(intensity):
            print("Vibrational intensity: " +  str(intensity))
            await my_buzz.vibrate_motors([intensity, 0, 0, intensity])
            sleep(qdelay)
            await my_buzz.vibrate_motors(motors_pause)
            sleep(qdelay)
             
             
        try:
            time.sleep(2)
            print('How can I help you?')
            while True:
                await asyncio.sleep(0.1)
                voice_data=mic_call2()
                if 'guide' or 'direct' in voice data:
                    speak('What object would you like me to direct you to?')
                    obj_of_interest = mic_call()
                        obj_of_interest = obj_of_interest.replace('.', '')
                        obj_of_interest = obj_of_interest.lower()
                        names, distances, positions = directional_guidance()
                        if obj_of_interest in names:
                            speak("I found a " + obj_of_interest)
                            index = names.index(obj_of_interest)
                            position = positions[index]
                            distance = distances[index]
                            angle = position * 60
                            speak("It's " + str(angle) + " degrees from your left")
                            if position <= 0.45:
                                intensity = int((.50 - position) * 500)
                                print('left buzz')
                                await pattern_left(intensity)
                            elif position < 0.45 and position > 0.55:
                                intensity = 200
                                print('straight buzz')
                                await pattern_straight(intensity)
                            elif position >= 0.55:
                                intensity = int((position - .50) * 500)
                                print('right buzz')
                                await pattern_right(intensity)
                        else:
                            print('not found buzz')
                    
                try:
                    speak(response)
                except AssertionError:
                    print('No text to speak')

        except KeyboardInterrupt:
            await my_buzz.resume_device_algorithm()
            pass
        

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
