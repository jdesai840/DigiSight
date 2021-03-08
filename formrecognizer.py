import os
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechRecognizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.vision.computervision import ComputerVisionClient


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

def docu_search():
    formy = 'https://i.pinimg.com/736x/e8/0e/f3/e80ef353d3cae38810e0d88c1e96bf9d.jpg'
    poller = form_recognizer_client.begin_recognize_content_from_url(formy)
    page = poller.result()
    search_array = []
    synthesizer.speak_text_async("Got it, scanning your document. What would you like me to search for?")
    scan_request = mic_call()
    scan_request = scan_request.replace('.', '')
    print(scan_request)
    for idx, content in enumerate(page):
        line_length = len(content.lines)
        for line_idx, line in enumerate(content.lines):
            if scan_request.lower() in line.text.lower():
                search_array.append(line_idx)
#                    print(content.lines[line_idx].text)
#                    print(content.lines[line_idx + 1].text)
#         synthesizer.speak_text_async("Here is your first search result.")
    for idx, content in enumerate(page):
        if search_array == []:
            synthesizer.speak_text_async("Couldn't find any results")
            break
        else:
            synthesizer.speak_text_async("Here is your first search result.")
            print(content.lines[search_array[0]].text)
            synthesizer.speak_text_async(content.lines[search_array[0]].text)
            print(content.lines[search_array[0] + 1].text)
            synthesizer.speak_text_async(content.lines[search_array[0] + 1].text)
            print(content.lines[search_array[0] + 2].text)
            synthesizer.speak_text_async(content.lines[search_array[0] + 2].text)

            synthesizer.speak_text_async("Would you like me to keep reading")
            query_response = mic_call()
            query_response = query_response.replace(".","")
            if query_response.lower() == "yes":
                for i in range(search_array[0] + 3, line_length-1):
                    synthesizer.speak_text_async(content.lines[i].text)
            elif query_response.lower() == "no":
                synthesizer.speak_text_async("Alrighty, let me know if you need anything else!")
            else:
                break

def describe():
    image_path = ('street.jpg')
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
        synthesizer.speak_text_async(spoken_text)
    
            
while True:
    press_button = input("Push the button")
    if press_button == "a":
        pick_feature = mic_call()
    elif press_button == "b":
        break
    
    if 'scan' in pick_feature.lower():
        docu_search()
    elif 'describe' in pick_feature.lower():
        describe()
        
        
        
# 
# def search_keyword(keyword):
#     for idx, content in enumerate(page):
#         for line_idx, line in enumerate(content.lines):
#             if keyword in line.text or keyword.lower() in line.text:
#                 print(content.lines[line_idx].text)
#                 print(content.lines[line_idx + 1].text)
# 
# search_keyword('philia')

# for idx, content in enumerate(page):
#     for line_idx, line in enumerate(content.lines):
#         print(line.text)
        
        
