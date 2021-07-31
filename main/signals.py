from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import Record, Notification, Prediction
from main.utils.predictor import States
from main.tasks import get_prediction


@receiver(post_save, sender=Record)
def send_websocket_message(sender, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            'data_results',
            {
                'type': 'chat_message',
                'rainfall_intensity': instance.rainfall_intensity,
                'rain_state': States.get_state(instance.rainfall_intensity)
            }
        )
        get_prediction.delay()

