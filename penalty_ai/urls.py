from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from detection import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('upload/', views.upload_video, name='upload_video'),  # 👈 Video upload view
]

# ✅ Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
