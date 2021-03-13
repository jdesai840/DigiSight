import os
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechRecognizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from PIL import Image


endpoint = "https://hackathonformrecog.cognitiveservices.azure.com/"
key = "10313789480245228ba917ab386fef94"
cog_key = '51aad77763794bd6a109a32167f646cb'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
speech_config = SpeechConfig(subscription="abd6a2f18dca4bba8374ac1887039dff", region="eastus")
audio_config = AudioOutputConfig(use_default_speaker=True)
synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
classifier = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))



def directional_guidance():
    image_path = ('phone.png')
    image_stream = open(image_path, 'rb')
    image = Image.open('phone.png')
    width, height = image.size
    features = ['Description', 'Objects', 'Categories']
    description = classifier.analyze_image_in_stream(image_stream, visual_features = features)
    print('hello')
    
import os
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechRecognizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from PIL import Image


endpoint = "https://hackathonformrecog.cognitiveservices.azure.com/"
key = "10313789480245228ba917ab386fef94"
cog_key = '51aad77763794bd6a109a32167f646cb'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
speech_config = SpeechConfig(subscription="abd6a2f18dca4bba8374ac1887039dff", region="eastus")
audio_config = AudioOutputConfig(use_default_speaker=True)
synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
classifier = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

def mic_call():
    speech_recognizer= SpeechRecognizer(speech_config=speech_config)
    print("speak into your microphone...")
    result = speech_recognizer.recognize_once_async().get()
    query = result.text
    print(query)
    return query

def directional_guidance():
    image_path = ('street.jpg')
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
        return name_array, obj_distance_array, position_array

# a, b, c = directional_guidance()
# print(a)
# print(b)
# print(c)

while True:
    press_button = input("Push the button")
    if press_button == "a":
        pick_feature = mic_call()
    elif press_button == "b":
        break
    
    if 'find' or 'direct' in pick_feature.lower():
        synthesizer.speak_text_async("Let me direct you to it. What would you like to find?")
        obj_of_interest = mic_call()
        obj_of_interest = obj_of_interest.replace('.', '')
        obj_of_interest = obj_of_interest.lower()
        names, distances, positions = directional_guidance()
        if obj_of_interest in names:
            synthesizer.speak_text_async("I found a " + obj_of_interest)
            index = names.index(obj_of_interest)
            position = positions[index]
            distance = distances[index]
            if position < 0.40:
                synthesizer.speak_text_async("It's to your left")
            elif position < 0.60 and position >= 0.40:
                synthesizer.speak_text_async("It's straight ahead")
            elif position >= 0.60:
                synthesizer.speak_text_async("It's to your right")
        else:
            synthesizer.speak_text_async("Sorry, couldn't find " + obj_of_interest)

    


