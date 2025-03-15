import json
from random import random, randint

import pika
from django.http import HttpResponse

from common.mqModels import AnalyseTask
from waterDetect import settings

def GetConnection():
    params = pika.ConnectionParameters(
        host=settings.RABBITMQ_CONFIG['host'],
        port=settings.RABBITMQ_CONFIG['port'],
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_CONFIG['username'],
            settings.RABBITMQ_CONFIG['password']
        )
    )
    connection = pika.BlockingConnection(params)
    return connection

def sendAnalyseTask(task: AnalyseTask):
    connection = GetConnection()
    channel = connection.channel()

    jsStr = json.dumps(task.toDict())

    channel.basic_publish(exchange='amq.direct',
                          routing_key='analyse',
                          body=jsStr)
    channel.close()
    connection.close()
