import pika

from waterDetect import settings

def initConsumer():
    print('initConsumer')
    # 连接到RabbitMQ服务器
    params = pika.ConnectionParameters(
        host=settings.RABBITMQ_CONFIG['host'],
        port=settings.RABBITMQ_CONFIG['port'],
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_CONFIG['username'],
            settings.RABBITMQ_CONFIG['password']
        )
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # 创建一个名为 'hello' 的队列
    channel.queue_declare(queue='test-queue', durable=True)

    # 告诉RabbitMQ使用callback函数来处理接收到的消息
    channel.basic_consume(queue='test-queue',
                          auto_ack=True,
                          on_message_callback=callback)
    channel.start_consuming()


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)