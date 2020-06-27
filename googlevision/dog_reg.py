import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types


def get_prediction(content):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations
    return labels


def is_dog(img):
    try:
        result = get_prediction(img)
        for label in result:
            print(label)
            if "dog" in label.description.lower():
                return True
    except Exception as e:
        print('detect error' + str(e))
    return False
