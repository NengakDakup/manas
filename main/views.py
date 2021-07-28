import json
from django.conf import settings
from django.db.models import Avg
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets

from main.models import Record, Prediction, Notification
from main.serializers import RecordSerializer
from main.utils.predictor import States 


class Index(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_obj = Record.objects.last()
        if current_obj:
            last_hour = current_obj.date_created.hour
            norm_last_hour = 12
            # Add in a QuerySet of all the books
            measured_rain_fall = list(reversed(
                Record.objects.values_list('rain_fall', flat=True).order_by('-id')[:last_hour]))
            predictions = list(reversed(
                Prediction.objects.values_list('prediction', flat=True).order_by('-id')[:12]))
            json_predictions = json.dumps([States.get_state_str(x) for x in predictions ])
            today = timezone.now()
            week = today - timezone.timedelta(days=7)
            daily_avg = Record.objects.filter(
                date_created__year=today.year, 
                date_created__month=today.month, 
                date_created__day=today.day).aggregate(
                    Avg("rain_fall"))['rain_fall__avg']
            weekly_avg = Record.objects.filter(
                date_created__gte=week
                ).aggregate(Avg("rain_fall"))['rain_fall__avg']
            context["daily_avg"] = "N/A" if not daily_avg else int(daily_avg)
            context["weekly_avg"] = int(weekly_avg)
            context['measured_rain_fall'] = json.dumps(measured_rain_fall)
            context['measured_drought_state'] = json.dumps([States.get_state(x) for x in measured_rain_fall])
            context['predictions'] = json_predictions
            context['time_type'] = 'am' if last_hour <= 12 else 'pm'
            context['next_state'] = None if not predictions else \
                    States.SHORT_NAMES[predictions[norm_last_hour - 1]]
            context['notifications'] = Notification.objects.filter(read=False)[:5]
            context['current_rain_fall'] = int((current_obj.rain_fall/settings.DRAIN_HEIGHT) * 100)
        return context


class RecordViewSet(viewsets.ModelViewSet):
    # ViewSets for the Data API 
    queryset = Record.objects.all() 
    serializer_class = RecordSerializer 
    
