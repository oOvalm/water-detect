import json
import logging

import pika

from common.db_model import FileType
from common.mqModels import AnalyseTask
from waterDetect import settings
from yolo.yolo_model.main import AnalyseTsVideoFolder, AnalyseImage, AnalyseImageWithPath


def initYoloConsumer():
    print('initConsumer, yolo-analyse')
    params = pika.ConnectionParameters(
        host=settings.RABBITMQ_CONFIG['host'],
        port=settings.RABBITMQ_CONFIG['port'],
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_CONFIG['username'],
            settings.RABBITMQ_CONFIG['password']
        ),
        heartbeat=60
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
SKIP = False
def consumeHandler(ch, method, properties, body):
    from database.models import FileInfo
    from common_service.fileService import FileManager
    if SKIP:
        return
    try:
        bodyDict = json.loads(body)
        mqInfo = AnalyseTask(**bodyDict)
        tsFolder = FileManager().GetTSFolder(mqInfo.fileUID)
        logger.info(f"consumer path: {tsFolder}, mqInfo: {mqInfo}")
        fileInfo = None
        try:
           fileInfo = FileInfo.objects.get(id=mqInfo.fileID, file_uid=mqInfo.fileUID)
        except FileInfo.DoesNotExist:
            logger.warning(f"file not exist, skip task: {mqInfo.fileID} {mqInfo.fileUID}")
            return
        filePath = FileManager().GetFilePath(fileInfo)
        if mqInfo.fileType == FileType.Video.value:
            analysedUID, size = AnalyseTsVideoFolder(tsFolder, mqInfo.fileUID)
            FileInfo.objects.createAnalysedFile(mqInfo.fileID, analysedUID, size)
        elif mqInfo.fileType == FileType.Image.value:
            analysedUID, size = AnalyseImageWithPath(filePath, mqInfo.fileUID)
            FileInfo.objects.createAnalysedFile(mqInfo.fileID, analysedUID, size)
        else:
            logger.error(f"not support file type {mqInfo.fileType}")
    except Exception as e:
        logger.error(f"consume error: {e}")

