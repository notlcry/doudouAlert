# coding:utf-8
import io
import uuid

from flask import Flask
from flask import request
from flask_restful import Api, reqparse, Resource
import dog_reg
import base64

app = Flask(__name__)
api = Api(app)


class VerificationCode(Resource):
    def __init__(self):
        pass

    @staticmethod
    def post():
        image = request.files['image']
        image_path = '/home/tmp.jpeg'
        file = image.save(image_path)
        with io.open(file, 'rb') as image_file:
            content = image_file.read()
        if dog_reg.is_dog(content):
            code = True
        else:
            code = False
        return {'code': code}


api.add_resource(VerificationCode, "/detect")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10050)
