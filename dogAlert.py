# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to classify objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import datetime
import io
import time
import numpy as np
import picamera
import os

from PIL import Image
from tflite_runtime.interpreter import Interpreter
import smtplib
from email.mime.text import MIMEText
from email.header import Header
# import cv2 as cv


def load_labels(path):
    with open(path, 'r') as f:
        return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


def classify(interpreter, image, top_k=5):
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # check the type of the input tensor
    floating_model = input_details[0]['dtype'] == np.float32

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    img = image.resize((width, height))

    # add N dim
    input_data = np.expand_dims(img, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - 127.5) / 127.5

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)
    print('--------------' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '----------------')
    print(results)
    print('------------------------------')
    if len(results) == 4:
        return results[1] / 256.0
    else:
        return 0


def classify_image(interpreter, image, top_k=10):
    """Returns a sorted array of classification results."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    # If the model is quantized (uint8 data), then dequantize the results
    if output_details['dtype'] == np.uint8:
        scale, zero_point = output_details['quantization']
        output = scale * (output - zero_point)

    ordered = np.argpartition(-output, top_k)

    return [(i, output[i]) for i in ordered[:top_k]]


def play_alert():
    # pygame.mixer.pre_init(44100, -16, 2, 2048)
    # effect = pygame.mixer.Sound('Alarm.wav')
    # effect.play()
    for i in range(3):
        os.system('/usr/bin/aplay /home/pi/dog/tensorflow/Alarm.wav')
    time.sleep(10)


def send_email():

    port = 25  # For SSL
    smtp_server = "smtp.163.com"
    sender_email = "yuhui_is@163.com"  # Enter your address
    receiver_email = "yuhui_is@163.com"  # Enter receiver address
    password = 'rainNT123'

    message = MIMEText("正文内容", 'plain', 'utf-8')
    message['From'] = "{0}<{1}>".format(sender_email, sender_email)
    message['To'] = receiver_email
    message['Subject'] = Header("豆豆进入请注意！", 'utf-8')

    smtpObj = smtplib.SMTP()
    smtpObj.connect(smtp_server, 25)  # 25 为 SMTP 端口号
    smtpObj.login(sender_email, password)
    smtpObj.sendmail(sender_email, receiver_email, message.as_string())
    print("邮件发送成功")
    smtpObj.quit()
    smtpObj.close()


def save_doudou(image, prob):
    file_jpg = '/home/pi/dog/images/doudou/dog_' \
               + datetime.datetime.now().strftime("%Y%m%d%H%M%S") \
               + "_" + str(prob*100) + '.jpeg'
    image.save(file_jpg)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model', help='File path of .tflite file.', required=True)
    parser.add_argument(
        '--labels', help='File path of labels file.', required=True)
    args = parser.parse_args()

    labels = load_labels(args.labels)

    interpreter = Interpreter(args.model)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    # _, height, width, _ = interpreter.get_input_details()[0]['shape']
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    with picamera.PiCamera(framerate=30) as camera:
        camera.rotation = 180
        camera.start_preview()
        try:
            stream = io.BytesIO()
            for _ in camera.capture_continuous(
                    stream, format='jpeg', use_video_port=True):
                stream.seek(0)
                # image = Image.open(stream).convert('RGB').resize((width, height),
                #                                                  Image.ANTIALIAS)
                image = Image.open(stream).convert('RGB')
                # camera.capture(stream, format='jpeg')
                box = (220, 0, 665, 760)
                region = image.crop(box)
                results = classify(interpreter, region)
                if results > 0.7:
                    save_doudou(region, results)
                    play_alert()
                    print("is doudou")
                    send_email()
                    print("doudou")
                #elif results > 0.3:
                #    save_doudou(region, results)
                #    print("maybe doudou")
                else:
                    print("no_doudou")
                stream.seek(0)
                stream.truncate()
                # camera.annotate_text = '%s %.2f\n%.1fms' % (labels[label_id], prob,
                #                                             elapsed_ms)
        finally:
            camera.stop_preview()


if __name__ == '__main__':
    main()