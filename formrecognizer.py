import os
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://hackathonformrecog.cognitiveservices.azure.com/"
key = "10313789480245228ba917ab386fef94"

form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))

formy = 'https://i.pinimg.com/736x/e8/0e/f3/e80ef353d3cae38810e0d88c1e96bf9d.jpg'

poller = form_recognizer_client.begin_recognize_content_from_url(formy)
page = poller.result()

for idx, content in enumerate(page):
    for line_idx, line in enumerate(content.lines):
        print(line.text)
