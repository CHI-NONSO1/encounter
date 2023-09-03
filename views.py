
import uuid
from django.shortcuts import render
from .models import Follower_Request, JissUser, Notification
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse
# from rest_framework.decorators import api_view
import tensorflow as tf
import numpy as np


def UserLogin(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = JissUser.objects.filter(email=email).values()
        user_pass = user[0]['password']
        usercheck = check_password(password, user_pass)
        if user and usercheck:
            tokenid = uuid.uuid4()
            JissUser.objects.filter(email=email).update(
                refresh_token=tokenid)

            access = JissUser.objects.filter(email=email).values()
            access_token = access[0]['refresh_token']

            return HttpResponseRedirect(reverse('encounterapp:home', args=[str(access_token)],))

        else:
            return render(request, 'encounterapp/jissUsers/login.html', {'error_message': "Your Password is not correct! ."})
    else:

        return render(request, 'encounterapp/jissUsers/login.html', {})


def follow(request, access_token):
    target_page = "encounterapp:home"
    if request.method == 'POST':
        follow_id = request.POST.get('user_id')
        adder = JissUser.objects.filter(refresh_token=access_token).values()
        adderID = adder[0]['id']
        follow = JissUser.objects.get(id=adderID)
        sender = JissUser.objects.get(id=adderID)
        recipient = JissUser.objects.get(id=follow_id)
        if follow.followings.filter(id=follow_id).exists():
            follow.followings.remove(follow_id)
            Follower_Request.objects.filter(requesting_id=follow_id).delete()
            Notification.objects.filter(recipient=follow_id).delete()
        else:
            follow.followings.add(follow_id)
            Follower_Request.objects.create(
                requesting_id=follow_id, requester_id=adderID)
            Notification.objects.create(
                recipient=recipient, sender=sender)

        return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))
    else:
        token = JissUser.objects.filter(refresh_token=access_token).values()
        userID = token[0]['id']
        followers = JissUser.objects.get(Q(id=userID))
        folow = followers.followings.all().values_list('id', flat=True)
        alusers = JissUser.objects.exclude(id=userID).exclude(id__in=folow)
        notify = JissUser.objects.get(id=userID)
        notificate = notify.notifications.filter(is_read=False)
        Notification.objects.filter(recipient=userID).update(is_read=True)
        context = {
            'access_token': access_token,
            'users': alusers,
            'notificate': notificate
        }

        serve_page = 'encounterapp/follow.html'
        return render(request, serve_page, context)


# @api_view(['POST'])
# def api_recommendations(request):
#     user_id = int(request.data['user_id'])

#     # Load the serialized model
#     model = tf.keras.models.load_model('encounter_model.keras')

#     # Preprocess input and make predictions
#     user_embedding = model.get_layer('user_embedding')(np.array([[user_id]]))
#     # Extract recommendations from the embedding
#     recommendations = user_embedding[0]

#     return JsonResponse({'recommendations': recommendations.tolist()})


def get_recommendations(request, access_token):
    if request.method == 'POST':
        user_id = int(request.POST.get('user_id'))

        # Load the serialized model
        model = tf.keras.models.load_model('encounter_model.keras')

        # Preprocess input and make predictions
        user_embedding = model.get_layer(
            'user_embedding')(np.array([[user_id]]))
        # Extract recommendations from the embedding
        recommendations = user_embedding[0]

        # Prepare context data
        context = {
            'user_id': user_id,
            'recommendations': recommendations.tolist(),
            'access_token': access_token
        }

        return render(request, 'encounterapp/encounter_suggest.html', context)
    else:
        context = {
            'access_token': access_token

        }
        return render(request, 'encounterapp/encounter_suggest.html', context)


def lender_borrower(request, access_token):
    context = {
        'access_token': access_token

    }
    return render(request, 'encounterapp/lender_borrower.html', context)
