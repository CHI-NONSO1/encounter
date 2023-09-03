from django.db.models import Q
from django.shortcuts import render
from encounterapp.models import EncaPost, JissUser
from django.http import HttpResponseRedirect
from django.urls import reverse


def search(request, access_token):
    user = JissUser.objects.filter(
        refresh_token=access_token).values()
    userID = user[0]['id']
    followers = JissUser.objects.get(id=userID)
    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()
    query = request.POST.get('query')
    user = JissUser.objects.filter(
        Q(firstname__icontains=query) |
        Q(lastname__icontains=query) |
        Q(email__icontains=query) |
        Q(phoneno__icontains=query) |
        Q(city__icontains=query) |
        Q(profession__icontains=query) |
        Q(address__icontains=query) |
        Q(rating__icontains=query)
    ).exclude(id=userID).values()

    post = EncaPost.objects.filter(
        Q(title__icontains=query) |
        Q(uploaded_at__icontains=query)

    ).values()

    if user:
        results = user
        context = {
            'access_token': access_token,
            'results': results,
            'user': user,
            'userID': userID,
            'follow': following,
            'encounters': encounters,


        }
        target_page = 'encounterapp/search/search_user_partial.html'
        return render(request, target_page, context)
    elif post:
        results = post
        context = {
            'access_token': access_token,
            'results': results,
            'userID': userID,
            'post': post,
            'follow': following,
            'encounters': encounters,


        }
        target_page = 'encounterapp/search_partial.html'
        return render(request, target_page, context)
    else:
        results = "Nothing found"

    context = {
        'access_token': access_token,
        'results': results,
        'userID': userID,
        'follow': following,
        'encounters': encounters,


    }
    target_page = 'encounterapp/search/search_empty_partial.html'
    return render(request, target_page, context)


def user_details(request, user_id, access_token):
    user = JissUser.objects.filter(
        refresh_token=access_token).values()
    userID = user[0]['id']
    user = JissUser.objects.filter(Q(id=user_id)).values()
    followers = JissUser.objects.get(id=userID)

    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()
    firstname = user[0]['firstname']
    lastname = user[0]['lastname']
    phoneno = user[0]['phoneno']
    email = user[0]['email']
    image = user[0]['image']

    context = {
        'access_token': access_token,
        'user_id': user_id,
        'firstname': firstname,
        'lastname': lastname,
        'phoneno': phoneno,
        'image': image,
        'email': email,
        'follow': following,
        'encounters': encounters,
        'userID': userID,




    }
    return render(request, 'encounterapp/search/user_details_partial.html', context)


def post_details(request, post_id, access_token):
    user = JissUser.objects.filter(Q(refresh_token=access_token)).values()
    user_id = user[0]['id']
    followers = JissUser.objects.get(id=user_id)

    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()
    post = EncaPost.objects.filter(Q(id=post_id)).values()
    post_likes = EncaPost.objects.get(Q(id=post_id))
    like = post_likes.like.all()
    share = post_likes.share.all()
    title = post[0]['title']
    timestamp = post[0]['timestamp']
    author_id = post[0]['user_id']
    post_image = post[0]['image']
    post_video = post[0]['video']
    content = post[0]['content']
    post_author = JissUser.objects.filter(Q(id=author_id)).values()
    author_firstname = post_author[0]['firstname']
    author_lastname = post_author[0]['lastname']
    author_image = post_author[0]['image']

    context = {
        'access_token': access_token,
        'post_id': post_id,
        'title': title,
        'timestamp': timestamp,
        'like': like,
        'share': share,
        'author_firstname': author_firstname,
        'author_lastname': author_lastname,
        'author_image': author_image,
        'post_image': post_image,
        'post_video': post_video,
        'content': content,
        'follow': following,
        'encounters': encounters

    }
    return render(request, 'encounterapp/search/search_detail_partial.html', context)
