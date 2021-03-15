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
import asyncio
from bleak import BleakClient
from bleak import discover
from neosensory_python import NeoDevice
from time import sleep
# picamera import required for raspberry pi deployment
# from picamera import PiCamera


endpoint = "https://hackathonformrecog.cognitiveservices.azure.com/"
key = "INSERT_KEY"
cog_key = 'INSERT_KEY'
cog_endpoint = 'https://cv-hackathon-test.cognitiveservices.azure.com/'
form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
speech_config = SpeechConfig(subscription="INSERT_KEY", region="eastus")
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
#   camera.capture('street.jpg')       # Only required if picamera is being utilized, for demo just use the image path we provided
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


def describe_image():
#   camera.capture('street.jpg')       # Only required if picamera is being utilized, for demo just use the image path we provided
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

def docu_read():
    synthesizer.speak_text_async("Reading text.")
    formy = 'https://i.pinimg.com/736x/e8/0e/f3/e80ef353d3cae38810e0d88c1e96bf9d.jpg'
    poller = form_recognizer_client.begin_recognize_content_from_url(formy)
    page = poller.result()
    for idx, content in enumerate(page):
        for line_idx, line in enumerate(content.lines):
            synthesizer.speak_text_async(line.text)
            
            
def docu_search():
#   camera.capture('form.jpg')       # Only required if picamera is being utilized, for demo just use the image path we provided
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
            while True:
                await asyncio.sleep(0.1)
                press_button = input("Push the button")
                if press_button == "a":
                    pick_feature = mic_call()
                    if 'scan' in pick_feature.lower():
                        docu_search()
                    elif 'describe' in pick_feature.lower():
                        describe_image()
                    elif 'read' in pick_feature.lower():
                        docu_read()
                    elif 'find' or 'direct' in pick_feature.lower():
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
                            angle = position * 60
                            synthesizer.speak_text_async("It's " + str(angle) + " degrees from your left")
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
                elif press_button == "b":
                    break

        except KeyboardInterrupt:
            await my_buzz.resume_device_algorithm()
            pass
        

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))


