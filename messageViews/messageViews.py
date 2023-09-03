from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ..models import EncaGroupChat, EncaGroupChatNotification, EncaGroups, MessageNotification, Message, JissUser
from django.db.models import Q


def chat(request, user_id, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    connectn = int(user_id)+int(userID)
    messages = Message.objects.filter(
        Q(connections=connectn)).order_by('timestamp').values()
    print(messages)
    context = {
        'messages': messages,
        'access_token': access_token,
        'user_id': user_id

    }
    return render(request, 'encounterapp/messaging/chat.html', context)


def instant_chat(request, connect_id, user_id, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']

    messages = Message.objects.filter(
        Q(connections=connect_id)).order_by('timestamp').values()
    context = {
        'access_token': access_token,
        'connectn': connect_id,
        'user_id': user_id,
        'senderid': userID,
        'messages': messages
    }
    return render(request, 'encounterapp/messaging/instant-chat.html', context)


def send_message(request, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']

    if request.method == 'POST':
        sender = JissUser.objects.get(id=userID)
        receiver_id = request.POST.get('user_id')
        content = request.POST.get('content')
        connect = int(userID)+int(receiver_id)
        receiver = get_object_or_404(JissUser, id=receiver_id)

        message, created = Message.objects.get_or_create(content=content, defaults={
            'sender': sender, 'receiver': receiver, 'content': content, 'connections': connect},)
        MessageNotification.objects.create(
            sender=sender, recipient=receiver, message=message)
        # Broadcast the message to the chat group using Channels
        # Implement your Channels logic here to send the message to other connected users

        return HttpResponseRedirect(reverse('encounterapp:chat', args=[receiver_id, access_token],))

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def send_group_message(request, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']

    if request.method == 'POST':
        sender = JissUser.objects.get(id=userID)
        receiver_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        content = request.POST.get('content')
        group = EncaGroups.objects.get(id=group_id)
        message = EncaGroupChat.objects.get_or_create(
            content=content,
            defaults={
                'sender': sender,
                'groupid': group_id,
                'group': group,
                'content': content
            },)
        EncaGroupChatNotification.objects.create(
            sender=sender, groupid=group_id, group=group, message=message)
        # Broadcast the message to the chat group using Channels
        # Implement your Channels logic here to send the message to other connected users

        return HttpResponseRedirect(reverse('encounterapp:chat', args=[receiver_id, access_token],))

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def get_messages(request, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    connection = get_object_or_404(Persons, id=userID)
    messages = Message.objects.filter(
        connection=connection).order_by('timestamp')
    message_data = [{'sender': message.sender.firstname, 'content': message.content,
                     'timestamp': str(message.timestamp)} for message in messages]
    return JsonResponse(request, {'messages': message_data})


def interact(request, access_token):
    serve_page = 'encounterapp/messaging/interact.html'
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    alusers = JissUser.objects.exclude(refresh_token=access_token)

    notify = JissUser.objects.get(id=userID)
    notificate = notify.notify.filter(is_read=False)
    MessageNotification.objects.filter(recipient=userID).update(is_read=True)
    context = {
        'senderid': userID,
        'access_token': access_token,
        'users': alusers,
        'notificate': notificate
    }
    return render(request, serve_page, context)


def chat_home(request, access_token):
    return render(request, "encounterapp/chat/base.html", {'access_token': access_token})


def room(request, room_name, access_token):
    return render(request, "encounterapp/chat/room.html", {"room_name": room_name, 'access_token': access_token})


def roomchat(request, room_name, group_id, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    senderid = token[0]['id']

    context = {
        'group_id': group_id,
        'access_token': access_token,
        'room_name': room_name,
        'senderid': senderid

    }
    return render(request, 'encounterapp/messaging/room-chat.html', context)
