import requests
from django.db import models
from django.conf import settings
from django.utils import timezone
from main.utils.nexmo import NexmoSMS
from main.utils.predictor import States


class Record(models.Model):
    """ Entry for All Data sent from Sensors """

    date_created = models.DateTimeField(auto_now_add=True)
    rain_fall = models.FloatField()

    def __str__(self):
        return f"{self.rain_fall} - {self.date_created}"

    @property
    def state(self):
        return States.get_state(self.rain_fall)


class Prediction(models.Model):
    """ 
    A History of All Predictions
    """
    STATES = (
        ('N', States.DROUGHT),
        ('A', States.ALMOST_DROUGHT), ('F', States.NORMAL),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    prediction = models.CharField(max_length=1, choices=STATES)
    date_predicted = models.DateTimeField()
    uid = models.UUIDField(editable=False)

    def __str__(self):
        return f"{self.get_prediction_display()} - {self.date_predicted}"

    def is_flood(self):
        return self.get_prediction_display() == States.DROUGHT


class Notification(models.Model):
    """ 
    Notification System both Emailing and SMS
    """
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    
    @classmethod
    def send(cls, prediction=None, sms=True):
        message = f"There is an impending Drought at {prediction.date_predicted.strftime('%D %H:%M:%S')}"
        notification = cls.objects.create(message=message)
        # TODO Send Email
        if sms:
            nexmo = NexmoSMS()
            nexmo.send_message(notification.message)
            requests.get(f"http://{settings.NODE_IP_ADDRESS}/update", 
                    params={"sleep_time", (prediction.date_predicted - timezone.now()).total_seconds})

