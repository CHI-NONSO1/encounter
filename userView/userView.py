import random
import string
from django.utils import timezone
from django.shortcuts import render
from encounterapp.models import Comment, EncaGroups, EncaPost, JissUser, Notification, SharedPost
from django.contrib.auth.hashers import make_password
from datetime import timedelta
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
import smtplib
from email.mime.text import MIMEText
from itertools import chain


def home(request, access_token):
    target_page = 'encounterapp/home.html'
    user = JissUser.objects.get(refresh_token=access_token)
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)
    groups = EncaGroups.objects.filter(memberid=userID).values()
    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()

    follow = followers.followings.all()

    notify = JissUser.objects.get(id=userID)

    notificate = notify.notifications.filter(is_read=False)

    posts = EncaPost.objects.filter(Q(user__in=follow) | Q(
        user=userID)).prefetch_related('comments__replies').order_by('-uploaded_at')[:4]
    shared_posts = SharedPost.objects.filter(Q(name__in=follow) | Q(name=userID)).prefetch_related(
        'post', 'name', 'shared_post_comments__shared_post_replies').order_by('-timestamp')

    all_posts = sorted(
        chain(shared_posts, posts),
        key=lambda item: item.timestamp,
        reverse=True
    )
    user_token = token[0]['refresh_token']
    firstname = token[0]['firstname']
    lastname = token[0]['lastname']
    phoneno = token[0]['phoneno']
    email = token[0]['email']
    image = token[0]['image']

    context = {
        'access_token': user_token,
        'firstname': firstname,
        'lastname': lastname,
        'phoneno': phoneno,
        'img': image,
        'email': email,
        'sponsored_post': sponsored_post,
        'userID': userID,
        'justexplained': justexplained,
        'follow': following,
        'notificate': notificate,
        'encounters': encounters,
        'groups': groups,
        'items': all_posts

    }

    return render(request, target_page, context)


def Dashbaord(request, access_token):
    target_page = 'encounterapp/dashboard/dashboard.html'
    token = JissUser.objects.filter(refresh_token=access_token).values()
    user = JissUser.objects.get(refresh_token=access_token)
    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)
    groups = EncaGroups.objects.filter(memberid=userID).values()
    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()

    posts = EncaPost.objects.filter(
        Q(user=userID)).order_by('-uploaded_at')[:4]
    comments = Comment.objects.all()
    shared = SharedPost.objects.filter(shared_with=user)
    notify = JissUser.objects.get(id=userID)
    notificate = notify.notifications.filter(is_read=False)
    user_token = token[0]['refresh_token']
    firstname = token[0]['firstname']
    lastname = token[0]['lastname']
    phoneno = token[0]['phoneno']
    email = token[0]['email']
    image = token[0]['image']

    context = {
        'access_token': user_token,
        'firstname': firstname,
        'lastname': lastname,
        'phoneno': phoneno,
        'img': image,
        'email': email,
        'userID': userID,
        'follow': following,
        'notificate': notificate,
        'encounters': encounters,
        'posts': posts,
        'comments': comments,
        'groups': groups


    }

    return render(request, target_page, context)


def UserRegister(request):
    verifyToken = "".join(random.choices(str(
        string.ascii_letters.encode('utf-8')), k=20))
    if request.method == 'POST':
        passwd = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        phoneno = request.POST.get('phoneno')
        password = make_password(passwd)
        image = request.FILES.get('file')
        if passwd == ' ' or confirm_password == ' ' or email == ' ' or firstname == ' ' or lastname == ' ' or phoneno == ' ':
            context = {
                'error_message': 'You need to enter real values'
            }
            return render(request, 'encounterapp/jissUsers/register.html', context)
        if passwd != confirm_password:
            context = {
                'error_message': 'Password and confirm password did not match'
            }
            return render(request, 'encounterapp/jissUsers/register.html', context)

        register, created = JissUser.objects.get_or_create(phoneno=phoneno, email=email, defaults={
            'email': email,
            'firstname': firstname,
            'lastname': lastname,
            'phoneno': phoneno,
            'password': password,
            'image': image,
            'verify_token': verifyToken
        })
        if created == False:
            context = {
                'error_message': 'Email or Phone number already exist!'
            }
            return render(request, 'encounterapp/jissUsers/register.html', context)

        if created == True:
            subject = "Email Subject"
            body = "An email has been sent to you to verify your email" + " " + \
                'http://localhost:8000/verify/' + verifyToken
            sender = "havefuninsixtys@gmail.com"
            recipients = [email]
            password = "gfoffxmwbiudobon"

            def send_email(subject, body, sender, recipients, password):
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(recipients)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                    smtp_server.login(sender, password)
                    smtp_server.sendmail(sender, recipients, msg.as_string())
                print("Message sent!")

            send_email(subject, body, sender, recipients, password)

            return HttpResponseRedirect(reverse("encounterapp:login"))

    else:
        return render(request, 'encounterapp/jissUsers/register.html', {})


def UserLogout(request, access_token):
    JissUser.objects.filter(refresh_token=access_token).update(
        refresh_token='Null')

    return HttpResponseRedirect(reverse("encounterapp:login"))


def verify_email(request, slug):

    if request.method == 'POST':
        verifytoken = request.POST.get('verify_token')
        token = JissUser.objects.filter(verify_token=verifytoken).values()
        userverifytoken = token[0]['verify_token']

        if userverifytoken:
            JissUser.objects.filter(verify_token=userverifytoken).update(
                verify_token='Null', isActive=1)

            return HttpResponseRedirect(reverse('encounterapp:verified'))

    else:
        return render(request, 'encounterapp/jissUsers/verify_form.html', {'slug': slug})


def verified_email(request):
    message = 'Thank you! your email is verified'
    return render(request, 'encounterapp/jissUsers/verified.html', {'msg': message})


def passwordform(request):
    verifyToken = "".join(random.choices(str(
        string.ascii_letters.encode('utf-8')), k=20))
    if request.method == 'POST':
        email = request.POST.get('email')
        token = JissUser.objects.filter(email=email).values()

        if token:
            JissUser.objects.filter(email=email).update(
                reset_token=verifyToken)
            subject = "Email Subject"
            body = "Follow the link to reset your password" + " " + \
                'http://localhost:8000/reset/' + verifyToken
            sender = "havefuninsixtys@gmail.com"
            recipients = [email]
            password = "gfoffxmwbiudobon"

            def send_email(subject, body, sender, recipients, password):
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(recipients)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                    smtp_server.login(sender, password)
                    smtp_server.sendmail(sender, recipients, msg.as_string())
                print("Message sent!")

            send_email(subject, body, sender, recipients, password)
            return HttpResponseRedirect(reverse('encounterapp:sent'))

    else:
        return render(request, 'encounterapp/jissUsers/resetpassword_form.html', {'msg': 'Error'})


def passwordreset(request, slug):
    if request.method == 'POST':
        reset_token = request.POST.get('reset_token')

        passwd = request.POST.get('password')
        confirm_passwd = request.POST.get('confirm_password')
        if passwd != confirm_passwd:
            return render(request, 'encounterapp/jissUsers/password_form.html', {'msg': 'password and confirm password did not match'})

        password = make_password(passwd)
        JissUser.objects.filter(reset_token=reset_token).update(
            password=password,
            reset_token=None)
        return HttpResponseRedirect(reverse("encounterapp:login"))
    else:
        return render(request, 'encounterapp/jissUsers/password_form.html', {'slug': slug})


def check_email(request):
    message = 'An email has been sent. follow the link in the email to reset your password'
    return render(request, 'encounterapp/jissUsers/email_form.html', {'msg': message, })


def notifications(request, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    userID = token[0]['id']
    followers = JissUser.objects.get(Q(id=userID))
    folow = followers.followings.all().values_list('id', flat=True)
    alusers = JissUser.objects.exclude(id=userID).exclude(id__in=folow)
    notify = JissUser.objects.get(id=userID)
    notificate = notify.notifications.filter(is_read=False)
    allnotificate = notify.notifications.filter()
    Notification.objects.filter(recipient=userID).update(is_read=True)
    context = {
        'access_token': access_token,
        'users': alusers,
        'notificate': notificate,
        'allnotificate': allnotificate
    }

    serve_page = 'encounterapp/notifications.html'
    return render(request, serve_page, context)
