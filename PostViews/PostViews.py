from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from moviepy.editor import VideoFileClip
from encounterapp.models import Comment, EncaGroups, EncaPost, EncaPostNotification, Hashtag, JissUser, SharedPost, SharedPostComment
from django.http import HttpResponseRedirect
from django.urls import reverse


def post(request, access_token):
    target_page = "encounterapp:dashboard"
    if request.method == 'POST':
        video = request.FILES.get('video')
        content = request.POST.get('content')
        title = request.POST.get('title')
        image = request.FILES.get('image')
        post = EncaPost()

        userid = JissUser.objects.get(
            refresh_token=access_token)
        user = JissUser.objects.filter(
            refresh_token=access_token).values()
        memberid = user[0]['id']
        post.user_id = user[0]['id']
        group_options = request.POST.getlist('groups')
        hashtag_names = request.POST.getlist('hashtags')

        if group_options != '':
            groups = EncaGroups.objects.filter(
                memberid=memberid, group_name__in=group_options)

            try:
                if video:
                    # Check video length
                    video_clip = VideoFileClip(video.temporary_file_path())
                    duration = video_clip.duration

                    if duration >= 70:
                        raise ValidationError(
                            'Video duration exceeds 60 seconds.')

                    post, created = EncaPost.objects.get_or_create(content=content,
                                                                   defaults={
                                                                       'title': title,
                                                                       'image': image,
                                                                       'video': video,
                                                                       'content': content,
                                                                       'user': userid
                                                                   },)
                    for hashtag_name in hashtag_names:
                        hashtag, created = Hashtag.objects.get_or_create(
                            name=hashtag_name)
                        post.hashtags.add(hashtag)
                    post.groups.add(*groups)
                    EncaPostNotification.objects.create(
                        user=userid, post_id=post.id)

                    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))
                else:

                    post, created = EncaPost.objects.get_or_create(content=content,
                                                                   defaults={
                                                                       'title': title,
                                                                       'image': image,
                                                                       'content': content,
                                                                       'user': userid
                                                                   },)
                    for hashtag_name in hashtag_names:
                        hashtag, created = Hashtag.objects.get_or_create(
                            name=hashtag_name)
                        post.hashtags.add(hashtag)

                    EncaPostNotification.objects.create(
                        user=userid, post_id=post.id)

                    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))

            except Exception as e:
                groups = EncaGroups.objects.filter(memberid=memberid).values()

                target_page = "encounterapp:dashboard"
                context = {
                    'groups': groups,
                    'access_token': access_token,
                    'error': e
                }
                return render(request, target_page, context)
        else:

            try:
                if video:
                    # Check video length
                    video_clip = VideoFileClip(video.temporary_file_path())
                    duration = video_clip.duration

                    if duration >= 70:
                        raise ValidationError(
                            'Video duration exceeds 60 seconds.')

                    post, created = EncaPost.objects.get_or_create(content=content,
                                                                   defaults={
                                                                       'title': title,
                                                                       'image': image,
                                                                       'video': video,
                                                                       'content': content,
                                                                       'user': userid
                                                                   },)
                    for hashtag_name in hashtag_names:
                        hashtag, created = Hashtag.objects.get_or_create(
                            name=hashtag_name)
                        post.hashtags.add(hashtag)
                    EncaPostNotification.objects.create(
                        user=userid, post_id=post.id)

                    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))
                else:
                    post, created = EncaPost.objects.get_or_create(content=content,
                                                                   defaults={
                                                                       'title': title,
                                                                       'image': image,
                                                                       'content': content,
                                                                       'user': userid
                                                                   },)
                    for hashtag_name in hashtag_names:
                        hashtag, created = Hashtag.objects.get_or_create(
                            name=hashtag_name)
                        post.hashtags.add(hashtag)

                    EncaPostNotification.objects.create(
                        user=userid, post_id=post)

                    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))

            except Exception as e:
                groups = EncaGroups.objects.filter(memberid=memberid).values()
                target_page = "encounterapp:dashboard"
                context = {
                    'groups': groups,
                    'access_token': access_token,
                    'error': e
                }
                return render(request, target_page, context)

    else:
        token = JissUser.objects.filter(refresh_token=access_token).values()
        user_id = token[0]['id']
        groups = EncaGroups.objects.filter(
            memberid=user_id).values()

        context = {
            'groups': groups,
            'access_token': access_token
        }

        target_page = "encounterapp:dashboard"
        return render(request, target_page, context)


def DeletePost(request, post_id, access_token):
    target_page = "encounterapp:dashboard"
    post = get_object_or_404(EncaPost, id=post_id)
    if post.image:
        post.image.delete()
    if post.video:
        post.video.delete()

    post.delete()
    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))


def SponsorPost(request, post_id, access_token):
    post = EncaPost.objects.filter(id=post_id)
    action = post.update(is_sponsored=True)
    if action:
        target_page = "encounterapp:dashboard"

        return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))


def like_post(request, post_id, access_token):
    target_page = "encounterapp:home"
    user = JissUser.objects.get(refresh_token=access_token)
    post = get_object_or_404(EncaPost, id=post_id)
    if user in post.like.all():
        post.like.remove(user)
    else:
        post.like.add(user)

    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))


def like_post_comment(request, comment_id, access_token):
    target_page = "encounterapp:home"
    user = JissUser.objects.get(refresh_token=access_token)
    comment = get_object_or_404(Comment, id=comment_id)

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)

    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))


def add_post_comment(request, post_id, access_token):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        post = get_object_or_404(EncaPost, id=post_id)
        comment_content = request.POST.get('comment')
        user = request.POST.get('user')
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
        Comment.objects.create(
            post=post, parent=parent_comment, content=comment_content, user_id=user)

    return HttpResponseRedirect(reverse("encounterapp:home", args=[str(access_token)],))


def add_comment_shared_post(request, shared_post_id, access_token):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        post = get_object_or_404(SharedPost, id=shared_post_id)
        comment_content = request.POST.get('comment')
        user = request.POST.get('user')
        if parent_id:
            parent_comment = get_object_or_404(SharedPostComment, id=parent_id)
        SharedPostComment.objects.create(
            shared_post=post, parent=parent_comment, content=comment_content, user_id=user)

    return HttpResponseRedirect(reverse("encounterapp:home", args=[str(access_token)],))


def hashtag_posts(request, hashtag_name, access_token):
    hashtag = Hashtag.objects.get(name=hashtag_name)
    posts = hashtag.posts.all()
    context = {'hashtag': hashtag,
               'posts': posts,
               'access_token': access_token,
               }
    return render(request, 'encounterapp/hashtag_posts.html', context)


def share_post(request, post_id, access_token):
    target_page = "encounterapp:home"
    user = JissUser.objects.get(refresh_token=access_token)
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)
    follow = followers.followings.all()
    follower_list = list(follow)
    post = EncaPost.objects.get(id=post_id)
    if request.method == 'POST':
        message = request.POST.get('message', '')
        hashtag_names = request.POST.getlist('hashtags')
        shared = SharedPost.objects.create(
            post=post, name=user, message=message)
        shared.shared_with.add(*follower_list)
        for hashtag_name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(
                name=hashtag_name)
            shared.hashtags.add(hashtag)
        post.share.add(user)

    return HttpResponseRedirect(reverse(target_page, args=[str(access_token)],))
