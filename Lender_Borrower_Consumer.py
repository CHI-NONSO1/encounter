import json
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np
import tensorflow as tf


class LenderBorrowerConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]['token']

        self.room_group_name = f"suggest_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.user_rating = [4.8, 4.5, 2.4]
        self.model = tf.keras.models.load_model(
            "lender_borrower.keras")
        self.prep_data = np.array(self.user_rating).reshape(1, -1)
        recommend = self.model.predict(self.prep_data)
        await self.send(text_data=json.dumps({
            'type': 'user_recommend',
            'recommend': recommend.tolist()
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_ratings = data['user_ratings']

        model = tf.keras.models.load_model(
            "lender_borrower.keras")
        pre_data = np.array(user_ratings).reshape(1, -1)
        recommend = model.predict(pre_data)
        print(recommend)

        await self.send(text_data=json.dumps({
            'type': 'user_recommendations',
            'recommendations': recommend.tolist()
        }))
