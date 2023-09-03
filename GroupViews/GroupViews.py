from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from encounterapp.models import EncaPost, EncaGroupPostNotification, EncaGroupRooms, EncaGroups, Invitation, JissUser


def group(request, access_token):
    serve_page = 'encounterapp/groups/group.html'
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userid = token[0]['id']
    groups = EncaGroups.objects.all().values()

    context = {
        'access_token': access_token,
        'groups': groups,
        'userid': userid

    }

    return render(request, serve_page, context)


def group_home(request, group_id, access_token):
    serve_page = 'encounterapp/groups/group-home.html'
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userid = token[0]['id']
    groups = EncaGroups.objects.filter(
        id=group_id).values_list('id', flat=True).values()
    posts = EncaPost.objects.filter(
        groups=group_id).order_by('-uploaded_at')[:4]

    rooms = EncaGroupRooms.objects.filter(groupid=group_id).values()

    members = EncaGroups.objects.get(
        id=group_id).members.all().values()

    notifications = EncaGroupPostNotification.objects.filter(
        user=userid, is_read=False)

    context = {
        'access_token': access_token,
        'groups': groups,
        'userid': userid,
        'posts': posts,
        'members': members,
        'notifications': notifications,
        'rooms': rooms


    }
    return render(request, serve_page, context)


def join_group(request, group_id, access_token):

    serve_page = 'encounterapp/groups/group.html'
    token = JissUser.objects.filter(refresh_token=access_token).values()
    newmember = JissUser.objects.get(refresh_token=access_token)
    userid = token[0]['id']
    memba = EncaGroups.objects.get(
        id=group_id).members.filter(id=userid)
    if memba:
        groups = EncaGroups.objects.filter(
            id=group_id).values_list('members', flat=True).values()

        context = {
            'access_token': access_token,
            'groups': groups,
            'userid': userid,
            'memba': memba

        }

        return render(request, serve_page, context)
    else:

        EncaGroups.objects.get(
            id=group_id).members.add(newmember)
        groups = EncaGroups.objects.filter(
            id=group_id).values_list('members', flat=True).values()
        memba = EncaGroups.objects.get(
            id=group_id).members.filter(id=userid)

        context = {
            'access_token': access_token,
            'groups': groups,
            'userid': userid,
            'memba': memba

        }

        return render(request, serve_page, context)


def creategroup(request, access_token):
    target_page = "encounterapp:groups"
    userid = JissUser.objects.get(refresh_token=access_token)
    memid = JissUser.objects.filter(refresh_token=access_token).values()
    memberid = memid[0]['id']
    if request.method == 'POST':
        group_name = request.POST.get('group-name')
        description = request.POST.get('description')
        group_image = request.FILES.get('group-image')
        group = EncaGroups.objects.filter(
            group_name=group_name).values()

        if group.exists():
            serve_page = 'encounterapp/groups/create-group.html'
            context = {
                'access_token': access_token,
                'error': 'Group Name Already exist!',
            }
            return render(request, serve_page, context)

        else:
            group = EncaGroups.objects.create(
                group_name=group_name, description=description, group_image=group_image, is_admin=True, memberid=memberid)
            group.members.add(userid)
            groupid = group.id

        return HttpResponseRedirect(reverse(target_page,  args=[str(access_token)],))
    else:
        context = {
            'access_token': access_token,
        }

        serve_page = 'encounterapp/groups/create-group.html'
        return render(request, serve_page, context)


def send_invitation(request, group_id, access_token):
    target_page = "encounterapp:group_home"
    userid = JissUser.objects.get(refresh_token=access_token)
    group = EncaGroups.objects.get(id=group_id)
    invitee_name = request.POST['invitee_name']
    invitee = JissUser.objects.get(firstname=invitee_name)
    Invitation.objects.create(
        group=group, inviter=userid, invitee=invitee)
    # You can also send an email notification to the invitee here if desired
    context = {
        'access_token': access_token,
        'groupid': group_id
    }

    return HttpResponseRedirect(reverse(target_page, context))


def leave_group(request, group_id, access_token):
    serve_page = 'encounterapp:groups'

    token = JissUser.objects.filter(refresh_token=access_token).values()
    member = JissUser.objects.get(refresh_token=access_token)
    userid = token[0]['id']
    EncaGroups.objects.get(
        id=group_id).members.remove(member)
    groups = EncaGroups.objects.filter(
        id=group_id).values_list('members', flat=True).values()

    return HttpResponseRedirect(reverse(serve_page,  args=[str(access_token)],))


def createroom(request, group_id, access_token):
    target_page = "encounterapp:groups"
    userid = JissUser.objects.get(refresh_token=access_token)
    group = EncaGroups.objects.get(id=group_id)
    memid = JissUser.objects.filter(refresh_token=access_token).values()
    memberid = memid[0]['id']
    if request.method == 'POST':
        room_name = request.POST.get('room-name')
        description = request.POST.get('description')
        room_image = request.FILES.get('room-image')
        room = EncaGroupRooms.objects.filter(
            room_name=room_name).values()

        if room.exists():
            serve_page = 'encounterapp/groups/create-room.html'
            context = {
                'access_token': access_token,
                'error': 'Room Name Already exist!',
            }
            return render(request, serve_page, context)

        else:
            room, createdAt = EncaGroupRooms.objects.get_or_create(room_name=room_name,
                                                                   defaults={
                                                                       'room_name': room_name, 'description': description, 'room_image': room_image, 'is_admin': True, 'memberid': memberid,
                                                                       'groupid': group_id, 'group': group
                                                                   }
                                                                   )
            room.members.add(userid)

        return HttpResponseRedirect(reverse(target_page,  args=[str(access_token)],))
    else:
        context = {
            'access_token': access_token,
            'group_id': group_id
        }

        serve_page = 'encounterapp/groups/create-room.html'
        return render(request, serve_page, context)
