# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import tensorflow as tf
from tensorflow import keras
from keras.layers import Embedding
import numpy as np


class EncounterSuggestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]['token']

        self.room_group_name = f"suggest_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'suggest_user':
            user_id = text_data_json['user_id']

            # Load the serialized model
            model = tf.keras.models.load_model('encounter_model.keras', custom_objects={
                                               'user_embedding': Embedding, 'item_embedding': Embedding})

            # Preprocess input and make predictions
            user_embedding = model.get_layer(
                'user_embedding')(np.array([[int(user_id)]]))
            # Extract recommendations from the embedding
            recommendations = user_embedding[0].numpy().tolist()

            await self.send_recommendations(recommendations)

    async def send_recommendations(self, recommendations):
        await self.send(text_data=json.dumps({
            'type': 'recommendations',
            'recommendations': recommendations
        }))
