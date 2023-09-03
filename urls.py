from django.urls import path, re_path

from . import views
from .userView import userView
from .messageViews import messageViews
from .PostViews import PostViews
from .GroupViews import GroupViews
from .SearchView import SearchView
from .InvestmentView import InvestmentView


app_name = 'encounterapp'
urlpatterns = [
    # ===================Reg/Login=========================

    path('', views.UserLogin, name='login'),

    # ======================Home=====================================
    path('register/', userView.UserRegister, name='register'),

    path('home/<uuid:access_token>/', userView.home, name='home'),
    path('logout/<uuid:access_token>/', userView.UserLogout, name='logout'),
    path('dashboard/<uuid:access_token>/',
         userView.Dashbaord, name='dashboard'),
    # =======================Post============================================
    path('post/<uuid:access_token>/',
         PostViews.post, name='post'),
    path('post/<int:post_id>/<uuid:access_token>/',
         PostViews.DeletePost, name='delete'),
    path('sponsor_post/<int:post_id>/<uuid:access_token>/',
         PostViews.SponsorPost, name='sponsor_post'),
    path('post/<int:post_id>/like/<uuid:access_token>/',
         PostViews.like_post, name='like_post'),
    path('post_comment/<int:comment_id>/comment/<uuid:access_token>/',
         PostViews.like_post_comment, name='like_post_comment'),

    path('post/<int:post_id>/comment/<uuid:access_token>/',
         PostViews.add_post_comment, name='post_comment'),
    path('hashtag_posts/<str:hashtag_name>/<uuid:access_token>/',
         PostViews.hashtag_posts, name='hashtag_posts'),
    path('share/<int:post_id>/<uuid:access_token>/',
         PostViews.share_post, name='share'),
    path('shared-post/<int:shared_post_id>/comment/<uuid:access_token>/',
         PostViews.add_comment_shared_post, name='add_comment_shared_post'),

    # ====================Verify Email===============================================
    path('verify/<slug:slug>/',
         userView.verify_email,  name='verify'),
    path('verified/',
         userView.verified_email,  name='verified'),

    # ====================Reset Password===============================================
    path('password-form/',
         userView.passwordform,  name='password-form'),
    path('sent/',
         userView.check_email,  name='sent'),
    re_path(r"^reset/(?P<slug>[\w\-]+)/",
            userView.passwordreset,  name='reset'),

    # =======================Follower============================================
    path('follow/<uuid:access_token>/',
         views.follow,  name='follow'),

    # =======================Notifications============================================
    path('notifications/<uuid:access_token>/',
         userView.notifications,  name='notifications'),
    # =======================Messaging============================================
    path('send_message/<uuid:access_token>/',
         messageViews.send_message, name='send_message'),
    path('get_messages/<uuid:access_token>/',
         messageViews.get_messages, name='get_messages'),
    path('chat/<int:user_id>/<uuid:access_token>/',
         messageViews.chat, name='chat'),
    path('interact/<uuid:access_token>/',
         messageViews.interact, name='interact'),
    path('room-chat/<uuid:access_token>/',
         messageViews.chat_home, name='room-chat'),
    path("room-chat/<str:room_name>/<int:group_id>/<uuid:access_token>/",
         messageViews.roomchat, name="room-chat"),

    path("chat/<str:room_name>/<uuid:access_token>/",
         messageViews.room, name="room"),

    # =======================Instant Messaging============================================
    path('send_message/<uuid:access_token>/',
         messageViews.send_message, name='send_message'),
    path('get_messages/<uuid:access_token>/',
         messageViews.get_messages, name='get_messages'),
    path('instant/<int:connect_id>/<int:user_id>/<uuid:access_token>/',
         messageViews.instant_chat, name='instant-chat'),
    path('interact/<uuid:access_token>/',
         messageViews.interact, name='interact'),
    path('room-chat/<uuid:access_token>/',
         messageViews.chat_home, name='room-chat'),
    path("chat/<str:room_name>/<uuid:access_token>/",
         messageViews.room, name="room"),

    # =======================Group============================================
    path('groups/<uuid:access_token>/',
         GroupViews.group, name='groups'),
    path('join-group/<int:group_id>/<uuid:access_token>/',
         GroupViews.join_group, name='join-group'),
    path('leave-group/<int:group_id>/<uuid:access_token>/',
         GroupViews.leave_group, name='leave-group'),
    path('create-group/<uuid:access_token>/',
         GroupViews.creategroup, name='create-group'),
    path('group-home/<int:group_id>/<uuid:access_token>/',
         GroupViews.group_home, name='group-home'),
    path('create-room/<int:group_id>/<uuid:access_token>/',
         GroupViews.createroom, name='create-room'),


    # =======================Comments============================================
    # =======================Recommendations============================================
    path('suggest/<uuid:access_token>/', views.get_recommendations,
         name='suggest'),
#     path('api_recommendations/', views.api_recommendations,
     #     name='api_recommendations'),
    path('lender_borrower/<uuid:access_token>/', views.lender_borrower,
         name='lender_borrower'),

    # =======================Search============================================
    path('search/<uuid:access_token>/', SearchView.search,
         name='search'),
    path('user_details/<int:user_id>/<uuid:access_token>/', SearchView.user_details,
         name='user_details'),
    path('post_details/<int:post_id>/<uuid:access_token>/', SearchView.post_details,
         name='post_details'),

    # =======================Investment ============================================
    path('investment_banking/<uuid:access_token>/', InvestmentView.investment_signup,
         name='investment_banking'),
    path('investment_base/<uuid:access_token>/',
         InvestmentView.investment_dashbaord, name='investment_base'),
    path('find_borrowers/<uuid:access_token>/',
         InvestmentView.find_borrower, name='find_borrowers'),
    path('find_investors/<uuid:access_token>/',
         InvestmentView.find_investors, name='find_investors'),
    path('borrower_detail/<int:user_id>/<uuid:access_token>/',
         InvestmentView.borrower_detail, name='borrower_detail'),
    path('investor_detail/<int:user_id>/<uuid:access_token>/',
         InvestmentView.investor_detail, name='investor_detail'),
    path('invest/<int:borrower_id>/<uuid:access_token>/',
         InvestmentView.invest, name='invest'),

    path('transfer_interest/<uuid:access_token>/',
         InvestmentView.interest_transfer, name='transfer_interest'),







]
