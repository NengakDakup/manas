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
    current_state = States.get_state(Record.objects.last().rain_fall)
    # Generate a Numpy Array of Records
    rain_fall_entries = np.array(Record.objects.values_list('rain_fall', flat=True))

    data = pd.DataFrame({'Rainfall': rain_fall_entries})
    transition_matrix = TransitionMatrix(data)

    predictor = MarkovChainPredictor(transition_matrix.values, transition_matrix.states)
    # For every predictions for every 3 seconds till 6hrs
    predictions = predictor.generate_states(current_state, no_predictions=7200)
    # All predictions for a markov model should use the same uid
    uid = uuid.uuid4()
    send_sms = True
    for i, prediction in enumerate(predictions):
        pred = Prediction.objects.create(
            uid=uid,
            prediction=prediction[0].upper(),
            date_predicted=timezone.now() + timezone.timedelta(hours=i)
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
