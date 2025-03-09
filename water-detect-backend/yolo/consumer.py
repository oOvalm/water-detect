import json
import logging

import pika

from common.mqModels import AnalyseTask
from common.models import FileType
from waterDetect import settings
from yolo.service import fileManager
from yolo.yolo_model.main import AnalyseVideo


def initYoloConsumer():
    pikaLogger = logging.getLogger('pika')
    pikaLogger.setLevel(logging.ERROR)
    print('initConsumer, yolo-analyse')
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
    channel.queue_declare(queue='yolo-analyse', durable=True)
    channel.basic_consume(queue='yolo-analyse',
                          auto_ack=True,
                          on_message_callback=consumeHandler)
    print('yolo-analyse init done, start consume')
    channel.start_consuming()

logger = logging.getLogger(__name__)

def consumeHandler(ch, method, properties, body):
    try:
        bodyDict = json.loads(body)
        mqInfo = AnalyseTask(**bodyDict)
        tsFolder = fileManager.GetTSFolder(mqInfo.fileUID)
        logger.info(f"consumer path: {tsFolder}, mqInfo: {mqInfo}")
        # TODO: 确认file状态
        if mqInfo.fileType == FileType.Video.value:
            AnalyseVideo(tsFolder, mqInfo.fileUID)
        else:
            logger.error(f"not support file type {mqInfo.fileType}")
    except Exception as e:
        logger.error(f"consume error: {e}")

