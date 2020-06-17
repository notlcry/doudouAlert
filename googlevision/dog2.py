# -*- coding: UTF-8 -*-

from google.cloud import automl_v1beta1

prediction_client = automl_v1beta1.PredictionServiceClient()


def get_prediction(content):
    project_id = '305237550374'
    model_id = 'ICN5607979892634288128'
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request.payload  # waits till request is returned


def is_dog(img):
    try:
        result = get_prediction(img)
        if len(result) > 0 and result[0].display_name == 'doudou':
            return True
        elif len(result) > 2:
            pass

    except Exception as e:
        print 'detect error' + str(e)
    return False
