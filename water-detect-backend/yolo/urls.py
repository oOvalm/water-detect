from django.urls import path

from yolo.views import GetAnalyseProcess

urlpatterns = [
    path('getAnalyseProcess/<str:fileUID>/', GetAnalyseProcess.as_view()),
]
