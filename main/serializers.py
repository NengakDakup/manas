from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from main.models import Record

class RecordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Record
        fields = ['rain_fall',]

