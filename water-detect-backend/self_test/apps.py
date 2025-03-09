import threading

from django.apps import AppConfig

from self_test.rocketmq_utils import initConsumer


class SelfTestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'self_test'

    def ready(self):
        thread = threading.Thread(target=initConsumer)
        thread.daemon = True
        thread.start()
