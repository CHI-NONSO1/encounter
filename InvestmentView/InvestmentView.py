import decimal
from django.shortcuts import render
from ..models import EncaPost, JissUser, Investment, Interest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Q


# ====Borrower Funds His Reservered Account With Total Borrowing Amount====
def next_interest_payment_date(nextpaymentdate):

    current_date = datetime.now().date()

    if nextpaymentdate is None:
        return True
    next_due_date = nextpaymentdate.date()
    if next_due_date - current_date <= timedelta(days=7):
        return True
    return False


def investment_dashbaord(request, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]

    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)

    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()

    notify = JissUser.objects.get(id=userID)

    notificate = notify.notifications.filter(is_read=False)
    borrower = JissUser.objects.get(refresh_token=access_token)
    investors = Investment.objects.filter(borrower=borrower)
    next_payment_date = borrower.next_payment_date
    next_due_date = None
    if borrower.reserved_account:
        next_due_date = next_interest_payment_date(next_payment_date)

    firstname = token[0]['firstname']
    lastname = token[0]['lastname']
    phoneno = token[0]['phoneno']
    email = token[0]['email']
    image = token[0]['image']
    investing = token[0]['investing']
    last_payment_date = token[0]['last_payment_date']
    working_account = token[0]['working_account']
    target_investment = token[0]['target_investment']
    duration = token[0]['duration']
    rate = token[0]['rate']
    reserved_account = token[0]['reserved_account']
    pay = 0
    for investor in investors:
        pay += float(investor.amount) * (rate/100)
    if pay == 0:
        interest_payable = 0
    else:
        interest_payable = (float(target_investment) * (rate/100) + pay)

    context = {
        'access_token': access_token,
        'firstname': firstname,
        'lastname': lastname,
        'phoneno': phoneno,
        'image': image,
        'email': email,
        'sponsored_post': sponsored_post,
        'userID': userID,
        'justexplained': justexplained,
        'follow': following,
        'notificate': notificate,
        'encounters': encounters,
        'investing': investing,
        'last_payment_date': last_payment_date,
        'working_account': working_account,
        'target_investment': target_investment,
        'duration': duration,
        'rate': rate,
        'reserved_account': reserved_account,
        'investors': investors,
        'interest_payable': decimal.Decimal(interest_payable).quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP),
        "payment": decimal.Decimal(interest_payable),
        'next_payment_date': next_payment_date,
        'next_due_date': next_due_date
    }

    serve_page = 'encounterapp/dashboard/investment_base.html'
    return render(request, serve_page, context)


def investment_signup(request, access_token):
    target_page = "encounterapp:investment_base"
    borrower = JissUser.objects.get(refresh_token=access_token)

    if request.method == 'POST':
        investment_type = request.POST.get('investment_type')

        target_amount = request.POST.get('target_amount')
        amount = request.POST.get('amount')
        interest_rate = request.POST.get('rate')
        duration = request.POST.get('duration')
        if investment_type == 'borrower':
            borrower.target_investment = int(target_amount)
            borrower.reserved_account = int(target_amount)
            borrower.duration = int(duration)
            borrower.rate = int(interest_rate)
            borrower.investing = True
            borrower.save()
        elif investment_type == 'lender':
            investor = JissUser.objects.get(refresh_token=access_token)
            investor.working_account += int(amount)
            investor.duration = int(duration)
            investor.rate = int(interest_rate)
            investor.investing = True
            investor.save()

            return HttpResponseRedirect(reverse(target_page,  args=[str(access_token)],))
    else:

        active = JissUser.objects.get(refresh_token=access_token)
        investing = active.investing
        if investing == True:
            serve_page = "encounterapp:investment_base"

            return HttpResponseRedirect(reverse(serve_page,  args=[str(access_token)],))

        else:
            context = {
                'access_token': access_token,
                'investing': investing,
            }

            serve_page = 'encounterapp/dashboard/investment_bank.html'
            return render(request, serve_page, context)


# ====Lender Transers From His Working Acct To Borrowers Working Account======


def invest(request, borrower_id, access_token):
    target_page = "encounterapp:investment_base"
    if request.method == 'POST':
        invest_amount = request.POST.get('amount')
        lender_account = JissUser.objects.get(refresh_token=access_token)
        lender_working_account = lender_account.working_account
        if lender_working_account >= int(invest_amount):
            borrower_account = JissUser.objects.get(id=borrower_id)
            borrower_account.working_account += int(invest_amount)
            borrower_account.save()
            lender_account.working_account -= int(invest_amount)
            lender_account.save()
            Investment.objects.create(
                investor=lender_account, borrower=borrower_account, amount=invest_amount)

            return HttpResponseRedirect(reverse(target_page,  args=[str(access_token)],))
    else:
        context = {
            'access_token': access_token,
            'borrower_id': borrower_id,

        }

        serve_page = 'encounterapp/dashboard/invest.html'
        return render(request, serve_page, context)

# ====Borrower Transers From His Working Acct To Reservered Acct for Monthly Interest Payment======


def process_monthly_remittance(borrower_id):
    borrower = JissUser.objects.get(id=borrower_id)
    interest_payable = (float(borrower.target_investment)
                        * (borrower.rate / 100))
    borrower.reserved_account -= decimal.Decimal(interest_payable)
    borrower.last_payment_date = datetime.now()
    borrower.next_payment_date = borrower.last_payment_date + \
        timedelta(days=30)
    borrower.save()

    investors = Investment.objects.filter(borrower=borrower)

    for investor in investors:
        interest_receivable = (float(investor.amount) * (borrower.rate / 100))
        investor.investor.working_account += decimal.Decimal(
            interest_receivable)
        investor.investor.save()
        Interest.objects.create(borrower=borrower, amount=interest_receivable)


def interest_transfer(request, access_token):
    target_page = "encounterapp:investment_base"
    if request.method == 'POST':
        borrowerid = JissUser.objects.filter(
            refresh_token=access_token).values()
        borrower_id = borrowerid[0]['id']
        amount = request.POST.get('amount')
        borrower_account = JissUser.objects.get(refresh_token=access_token)
        borrower_account.reserved_account += int(amount)
        borrower_account.save()
        process_monthly_remittance(borrower_id)

        return HttpResponseRedirect(reverse(target_page,  args=[str(access_token)],))
    else:
        context = {
            'access_token': access_token,

        }

        serve_page = 'encounterapp/dashboard/interest_transfer.html'
        return render(request, serve_page, context)

# ====Borrower Process Monthly Interest Payment From His Reservered Account T Lender Working Acct======


def find_investors(request, access_token):
    investors = JissUser.objects.filter(Q(target_investment=0, investing=True))
    token = JissUser.objects.filter(refresh_token=access_token).values()
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]

    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)

    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()

    notify = JissUser.objects.get(id=userID)

    notificate = notify.notifications.filter(is_read=False)
    context = {
        'access_token': access_token,
        'investors': investors,
        'userID': userID,
        'justexplained': justexplained,
        'follow': following,
        'notificate': notificate,
        'encounters': encounters,
        'sponsored_post': sponsored_post,


    }
    return render(request, 'encounterapp/dashboard/investors_partial.html', context)


def find_borrower(request, access_token):
    borrowers = JissUser.objects.filter(
        Q(target_investment__gt=0, investing=True))
    token = JissUser.objects.filter(refresh_token=access_token).values()
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]

    userID = token[0]['id']
    followers = JissUser.objects.get(id=userID)

    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()

    notify = JissUser.objects.get(id=userID)

    notificate = notify.notifications.filter(is_read=False)
    context = {
        'access_token': access_token,
        'borrowers': borrowers,
        'userID': userID,
        'justexplained': justexplained,
        'follow': following,
        'notificate': notificate,
        'encounters': encounters,
        'sponsored_post': sponsored_post,


    }
    return render(request, 'encounterapp/dashboard/borrowers_partial.html', context)


def investor_detail(request, user_id, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]

    userid = token[0]['id']
    user = JissUser.objects.filter(Q(id=user_id)).values()
    followers = JissUser.objects.get(id=user_id)
    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()
    firstname = user[0]['firstname']
    lastname = user[0]['lastname']
    image = user[0]['image']
    duration = user[0]['duration']
    rate = user[0]['rate']

    context = {
        'access_token': access_token,
        'investorid': user_id,
        'firstname': firstname,
        'lastname': lastname,
        'image': image,
        'follow': following,
        'encounters': encounters,

        'duration': duration,
        'rate': rate,
        'sponsored_post': sponsored_post,
        'justexplained': justexplained,
        'userid': userid

    }
    return render(request, 'encounterapp/dashboard/investors_detail_partial.html', context)


def borrower_detail(request, user_id, access_token):
    token = JissUser.objects.filter(refresh_token=access_token).values()
    sponsored_post = EncaPost.objects.filter(is_sponsored=True, timestamp__gte=timezone.now(
    ) - timedelta(hours=72)).order_by('-uploaded_at')[:5]
    justexplained = EncaPost.objects.filter(timestamp__gte=timezone.now(
    ) - timedelta(hours=96)).order_by('-uploaded_at')[:5]

    userid = token[0]['id']
    user = JissUser.objects.filter(Q(id=user_id)).values()
    followers = JissUser.objects.get(id=user_id)
    following = followers.followings.all().distinct().count()
    encounters = JissUser.objects.filter(
        followings=followers).distinct().count()
    firstname = user[0]['firstname']
    lastname = user[0]['lastname']
    image = user[0]['image']
    last_payment_date = user[0]['last_payment_date']
    duration = user[0]['duration']
    rate = user[0]['rate']

    context = {
        'access_token': access_token,
        'borrowerid': user_id,
        'firstname': firstname,
        'lastname': lastname,
        'image': image,
        'follow': following,
        'encounters': encounters,
        'last_payment_date': last_payment_date,
        'duration': duration,
        'rate': rate,
        'sponsored_post': sponsored_post,
        'justexplained': justexplained,
        'userid': userid

    }
    return render(request, 'encounterapp/dashboard/borrowers_detail_partial.html', context)
