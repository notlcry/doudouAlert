# coding:utf-8
import os
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
        # str_64 = request.data
        # image = base64.decodestring(str_64)
        if dog_reg.is_dog(image):
            code = True
        else:
            code = False
        return {'code': code}


api.add_resource(VerificationCode, "/detect")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10050)
