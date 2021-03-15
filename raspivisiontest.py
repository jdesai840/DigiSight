#Raspberry Pi Azure Vision test

from time import sleep
from picamera import PiCamera
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os

cog_key = '51aad77763794bd6a109a32167f646cb'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
classifier = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
sleep(1)


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
        
while True:
    press_button = input("Push the button")
    if press_button == "a":
        description = describe_image()
        print(description)
    else press_button == "b":
        break
    
