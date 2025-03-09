from random import random, randint

import pika
from django.http import HttpResponse

from waterDetect import settings
connection = None
def getConnection():
    global connection
    if connection is None:
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

def send_message(request):
    connection = getConnection()
    channel = connection.channel()

    channel.queue_declare(queue='test-queue', durable=True)
    # 发送消息到队列
    channel.basic_publish(exchange='amq.direct',
                          routing_key='test',
                          body=str(randint(1, 1000000)))

    print(" [x] Sent 'Hello, RabbitMQ!'")
    channel.close()
    return HttpResponse('Message sent!')
