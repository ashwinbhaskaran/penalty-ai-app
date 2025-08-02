# detection/urls.py
from django.urls import path
from .views import (
    home_view,
    upload_video,
    detection_results
)

urlpatterns = [
    path('', home_view, name='home'),
    path('upload/', upload_video, name='upload_video'),
    path('results/', detection_results, name='results'),
]