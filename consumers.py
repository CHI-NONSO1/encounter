import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.db.models import Q
from encounterapp.models import EncaGroupChat, EncaGroupChatNotification, EncaGroups, JissUser, Message, MessageNotification
from django.core.serializers import serialize


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = await self.get_name()
        print(self.username)
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'prev_chat': await self.get_prev_chat(self.room_name),

        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    # Receive message from WebSocket

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        if message_type == 'delete_chat':
            chatid = text_data_json.get('chatid')
            await self.delete_chat(chatid)
        if message_type == 'chat_message':
            message = text_data_json["message"]
            group_id = text_data_json["group_id"]
            senderid = text_data_json["senderId"]
            roomname = text_data_json["roomname"]
            newchat = await self.save_message(senderid, group_id, message, roomname)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", 'message': {
                    "content": message, 'id': newchat.id, 'senderid': senderid, 'group_id': newchat.groupid}}
            )

    async def delete_chat(self, chatid):
        await self.removechat(chatid)
        await self.send(text_data=json.dumps({
            'type': 'chat_deleted',
            'chatid': chatid,
        }))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_deleted',
                'chatid': chatid,
            }
        )

    # Receive message from room group

    async def chat_message(self, event):
        message = event["message"]["content"]
        senderid = event["message"]["senderid"]
        group_id = event["message"]["group_id"]
        msgid = event["message"]["id"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': {"content": message, 'senderid': senderid, 'group_id': group_id, 'msgid': msgid}}))

    async def chat_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_deleted',
            'chatid': event['chatid'],
        }))

    @database_sync_to_async
    def get_name(self):
        return JissUser.objects.all()[0].firstname

    @database_sync_to_async
    def save_message(self, senderid, group_id, content, roomname):
        sender = JissUser.objects.get(id=senderid)
        group = EncaGroups.objects.get(id=group_id)

        message, created = EncaGroupChat.objects.get_or_create(content=content, defaults={
            'sender': sender, 'group': group, 'content': content, 'groupid': group_id, 'room_name': roomname},)
        EncaGroupChatNotification.objects.create(
            sender=sender, group=group, message=message, groupid=group_id, room_name=roomname)
        return message

    @database_sync_to_async
    def get_prev_chat(self, roomname):
        messages = EncaGroupChat.objects.filter(
            Q(room_name=roomname)
        ).order_by('timestamp')
        serializedata = serialize('json', messages, fields=(
            'content', 'sender', 'room_name', 'groupid', 'timestamp'))
        serializedata = json.loads(serializedata)

        return serializedata

    @database_sync_to_async
    def removechat(self, chatid):
        EncaGroupChat.objects.filter(
            id=chatid).delete()


class InstantChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]['connectid']

        self.room_group_name = f"instant_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Send previous messages to the client
        await self.accept()
        await self.send(text_data=json.dumps({
            'prev_message': await self.get_previous_messages(self.room_name),

        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    # Receive message from WebSocket

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        if message_type == 'delete_chat':
            chatid = text_data_json.get('chatid')
            await self.delete_chat(chatid)
        if message_type == 'chat_message':

            message = text_data_json["message"]
            senderid = text_data_json["senderid"]
            sender_id = text_data_json["sender_id"]
            receiverid = text_data_json["receiverid"]

            newchatid = await self.send_message(senderid, receiverid, message)
            print(newchatid.id)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": {
                    'content': message, 'sender_id': sender_id, 'receiverid': receiverid, 'id': newchatid.id}}
            )

    async def delete_chat(self, chatid):
        await self.removechat(chatid)
        await self.send(text_data=json.dumps({
            'type': 'chat_deleted',
            'chatid': chatid,
        }))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_deleted',
                'chatid': chatid,
            }
        )

    # Receive message from room group

    async def chat_message(self, event):

        message = event["message"]["content"]
        sender_id = event["message"]["sender_id"]
        receiverid = event["message"]["receiverid"]
        msgid = event["message"]["id"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": {"content": message, 'sender_id': sender_id, 'receiverid': receiverid, 'msgid': msgid}}))

    async def chat_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_deleted',
            'chatid': event['chatid'],
        }))

    @database_sync_to_async
    def send_message(self, senderid, receiverid, content):
        sender = JissUser.objects.get(refresh_token=senderid)
        chat_sender = JissUser.objects.filter(refresh_token=senderid).values()
        sender_id = chat_sender[0]['id']
        connect = int(sender_id)+int(receiverid)
        receiver = get_object_or_404(JissUser, id=receiverid)

        message, created = Message.objects.get_or_create(content=content, defaults={
            'sender': sender, 'receiver': receiver, 'content': content, 'connections': connect},)
        MessageNotification.objects.create(
            sender=sender, recipient=receiver, message=message)
        return message

    @database_sync_to_async
    def get_previous_messages(self, connectid):
        messages = Message.objects.filter(
            Q(connections=connectid)
        ).order_by('timestamp')
        sd = serialize('json', messages, fields=(
            'content', 'sender', 'receiver', 'timestamp'))
        sd = json.loads(sd)

        return sd

    @database_sync_to_async
    def removechat(self, chatid):
        Message.objects.filter(
            id=chatid).delete()
