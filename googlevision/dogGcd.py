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
import requests
import argparse
import datetime
import io
import time
import picamera
import os

from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def classify(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    url = "http://35.206.250.159:10050/detect"
    payload = {}
    files = [
        ('image', img_byte_arr)
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.json()


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


def save_doudou(image, prob=1):
    file_jpg = '/home/pi/dog/images/doudou/dog_' \
               + datetime.datetime.now().strftime("%Y%m%d%H%M%S") \
               + "_" + str(prob*100) + '.jpeg'
    image.save(file_jpg)


def main():

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
                results = classify(region)
                if results['code']:
                    save_doudou(region)
                    play_alert()
                    print("is doudou")
                    send_email()
                    print("doudou")
                else:
                    print("no_doudou")
                stream.seek(0)
                stream.truncate()
                # camera.annotate_text = '%s %.2f\n%.1fms' % (labels[label_id], prob,
                #                                             elapsed_ms)
        except Exception as e:
            print(e)
        finally:
            camera.stop_preview()


if __name__ == '__main__':
    main()
