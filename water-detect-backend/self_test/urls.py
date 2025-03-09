from django.urls import path

from self_test.views import send_message

urlpatterns = [
    path('send/', send_message, name='send_message'),
]