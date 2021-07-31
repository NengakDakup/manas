""" 
Celery Tasks 
"""

import uuid
import numpy as np
import pandas as pd
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.utils import timezone
from main.models import Record, Prediction, Notification
from main.utils.predictor import TransitionMatrix, MarkovChainPredictor, States


@shared_task
def get_prediction():
    """
    Get hourly prediction and update graphs
    """
    if Record.objects.count() <= 0:
        print("No data yet, prediction cannot happen")
        return
    current_state = States.get_state(Record.objects.last().rainfall_intensity)
    # Generate a Numpy Array of Records
    rainfall_intensity_entries = np.array(Record.objects.values_list('rainfall_intensity', flat=True))

    data = pd.DataFrame({'Rainfall': rainfall_intensity_entries})
    transition_matrix = TransitionMatrix(data)

    predictor = MarkovChainPredictor(transition_matrix.values, transition_matrix.states)
    # For every predictions for every 10 hrs
    predictions = predictor.generate_states(current_state, no_predictions=10)
    # All predictions for a markov model should use the same uid
    uid = uuid.uuid4()
    send_sms = True
    for i, prediction in enumerate(predictions):
        pred, created = Prediction.objects.get_or_create(
            date_predicted=timezone.now() + timezone.timedelta(hours=i),
            defaults={
                "uid":uid, 
                "prediction": prediction[0].upper()
            }
        )

        if pred.is_drought():
            # Send SMS once after a set of prediction
            # Don't bump the user with excess SMSs
            Notification.send(prediction=pred, sms=send_sms)
            send_sms = False
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'data_results',
        {
            'type': 'prediction_message',
            'prediction_update': 'true'
        }
    )
