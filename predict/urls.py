"""predict URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.views import Index, RecordViewSet, record_insert
from rest_framework import routers

# API Router
router = routers.DefaultRouter()
router.register(r'data', RecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('record/add/api/', record_insert, name="record-insert"),
    path('', Index.as_view(), name="index"),
]
