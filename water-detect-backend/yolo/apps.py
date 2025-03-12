import threading

from django.apps import AppConfig

# from yolo.consumer import initYoloConsumer


class YoloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'yolo'
    def ready(self):
        pass
        # thread = threading.Thread(target=initYoloConsumer)
        # thread.daemon = True
        # thread.start()

