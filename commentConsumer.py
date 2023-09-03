
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from encounterapp.models import Comment, EncaPost, JissUser, SharedPost, SharedPostComment


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["token"]
        self.room_group_name = f"group_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'comment_message':
            comment = data['comment']
            userid = data['userid']
            postid = data['postid']
            parent_id = data['parent_id']
            firstname = data['firstname']
            lastname = data['lastname']
            user_image = data['image']
            shared_post_id = data['shared_post_id']
            newcomment = await self.post_comment(userid, postid, parent_id, firstname, lastname, user_image, comment, shared_post_id)

            # Send the comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment_message',
                    'comment': comment,
                    'userid': userid,
                    'postid': postid,
                    'firstname': firstname,
                    'lastname': lastname,
                    'image': user_image,
                    'parent_id': parent_id,
                    'shared_post_id': shared_post_id,
                    'commentid': newcomment.id,


                }
            )

        if message_type == 'like_post':
            userid = data['userid']
            postid = data['postid']
            like = await self.like__post(userid, postid)

            # Send the comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'like_post',
                    'userid': userid,
                    'postid': postid,
                    'like': like,
                }
            )

        if message_type == 'like_comment':
            userid = data['userid']
            commentid = data['commentid']
            like = await self.like__comment(userid, commentid)

            # Send the comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'like_comment',
                    'userid': userid,
                    'commentid': commentid,
                    'like': like,
                }
            )

        if message_type == 'get_comment':
            postid = data['itemid']
            userid = data['userid']
            sharedpost_id = data['sharedpost_id']
            await self.get_comment_prev(postid, sharedpost_id, userid)

        if message_type == 'delete_comment':
            userid = data['userid']
            commentid = data['comment_id']
            postid = data['postid']
            shared_post_id = data['shared_post_id']

            await self.delete__comment(commentid, postid, shared_post_id)
            # Send the comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'delete_comment',
                    'userid': userid,
                    'commentid': commentid,
                    'postid': postid,
                    'shared_post_id': shared_post_id,
                }
            )

    async def comment_message(self, event):
        comment = event['comment']
        userid = event['userid']
        postid = event['postid']
        parent_id = event['parent_id']
        firstname = event['firstname']
        lastname = event['lastname']
        image = event['image']
        shared_post_id = event['shared_post_id']
        commentid = event['commentid']

        # Send the comment to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'comment_message',
            'comment': comment,
            'userid': userid,
            'postid': postid,
            'parent_id': parent_id,
            'firstname': firstname,
            'lastname': lastname,
            'image': image,
            'shared_post_id': shared_post_id,
            'commentid': commentid,

        }))

    async def like_post(self, event):
        userid = event['userid']
        postid = event['postid']
        like = event['like']
        # Send the comment to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'like_post',
            'userid': userid,
            'postid': postid,
            'like': like,

        }))

    async def like_comment(self, event):
        userid = event['userid']
        commentid = event['commentid']
        like = event['like']

        # Send the comment to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'like_comment',
            'userid': userid,
            'commentid': commentid,
            'like': like,

        }))

    async def delete_comment(self, event):
        userid = event['userid']
        commentid = event['commentid']
        postid = event['postid']
        shared_post_id = event['shared_post_id']
        # Send the comment to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete_comment',
            'userid': userid,
            'commentid': commentid,
            'postid': postid,
            'shared_post_id': shared_post_id,

        }))

    async def get_comment_prev(self, postid, sharedpost_id, userid):
        comment = await self.get_prev_comments(postid, sharedpost_id)
        await self.send(text_data=json.dumps({
            'type': 'get_comment',
            'comment': comment,
        }))

    async def get_comment(self, event):
        await self.send(text_data=json.dumps({
            'type': 'get_comment',
            'comment': event['comment'],

        }))

    @database_sync_to_async
    def get_prev_comments(self, postid, sharedpost_id):

        if postid:
            comments = Comment.objects.filter(
                Q(post=postid)
            ).order_by('created_at')
            serializecomments = serialize('json', comments)
            serializecomments = json.loads(serializecomments)
            return serializecomments
        if sharedpost_id:

            comments = SharedPostComment.objects.filter(
                Q(shared_post=sharedpost_id)
            ).order_by('created_at')

            serializecomments = serialize('json', comments)
            serializecomments = json.loads(serializecomments)
            return serializecomments

    @database_sync_to_async
    def post_comment(self, userid, postid, parent_id, firstname, lastname, user_image, content, shared_post_id):
        user = JissUser.objects.get(id=userid)
        if postid:
            post = EncaPost.objects.get(id=postid)
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                message, created = Comment.objects.get_or_create(content=content, defaults={
                    'user': user, 'firstname': firstname, 'lastname': lastname, 'user_image': user_image, 'parent': parent_comment, 'post': post, 'content': content},)
            else:
                message, created = Comment.objects.get_or_create(content=content, defaults={
                    'user': user, 'firstname': firstname, 'lastname': lastname, 'user_image': user_image, 'post': post, 'content': content},)

            return message
        if shared_post_id:
            shared_post = SharedPost.objects.get(id=shared_post_id)
            if parent_id:
                parent_comment = get_object_or_404(
                    SharedPostComment, id=parent_id)
                message, created = SharedPostComment.objects.get_or_create(content=content, defaults={
                    'user': user, 'firstname': firstname, 'lastname': lastname, 'user_image': user_image, 'parent': parent_comment, 'shared_post': shared_post, 'content': content},)
            else:
                message, created = SharedPostComment.objects.get_or_create(content=content, defaults={
                    'user': user, 'firstname': firstname, 'lastname': lastname, 'user_image': user_image, 'shared_post': shared_post, 'content': content},)

            return message

    @database_sync_to_async
    def delete__comment(self, commentid, postid, shared_post_id):
        print(postid, shared_post_id)
        if postid != 'undefined':
            Comment.objects.filter(id=commentid).delete()
        if shared_post_id != 'undefined':
            SharedPostComment.objects.filter(id=commentid).delete()

    @database_sync_to_async
    def like__post(self, userid, postid):
        post = get_object_or_404(EncaPost, id=postid)
        user = JissUser.objects.get(id=userid)
        if user in post.like.all():
            post.like.remove(user)
            like = -1
        else:
            post.like.add(user)
            like = 1

        return like

    @database_sync_to_async
    def like__comment(self, userid, commentid):
        comment = get_object_or_404(Comment, id=commentid)
        user = JissUser.objects.get(id=userid)
        if user in comment.likes.all():
            comment.likes.remove(user)
            like = -1
        else:
            comment.likes.add(user)
            like = 1

        return like
