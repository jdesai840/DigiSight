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
    
    if description.objects:
        for object in description.objects:
            r = object.rectangle
            obj_area = (r.w * r.h)
            img_area = width * height
            obj_distance = obj_area/img_area
            x_coord = (r.x + (r.w)/2)
            name = object.object_property
            position = x_coord/width
            print(name)
            print(obj_distance)
            print(position) 


directional_guidance()

