from django.urls import re_path

from .Lender_Borrower_Consumer import LenderBorrowerConsumer
from .EncounterSuggestConsumer import EncounterSuggestConsumer
from .commentConsumer import CommentConsumer


from encounterapp import consumers


websocket_urlpatterns = [
    #     re_path(r"ws/chat/(?P<room_name>\w+)/(?P<token>\w+)/$",
    re_path(r"ws/room-chat/(?P<room_name>\w+)/(?P<group_id>\w+)/(?P<token>\w+)/$",
            consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/instant/(?P<connectid>\w+)/(?P<user_id>\w+)/(?P<token>\w+)/$",
            consumers.InstantChatConsumer.as_asgi()),
    #     re_path(r"ws/instant/(?P<recipientid>\w+)/(?P<token>\w+)/$",
    #             consumers.InstantChatConsumer.as_asgi()),
    re_path(r"ws/add_comment/(?P<token>\w+)/$",
            CommentConsumer.as_asgi()),
    re_path(r"ws/suggest/(?P<token>\w+)/$",
            EncounterSuggestConsumer.as_asgi()),

    re_path(r"ws/lender_borrower/(?P<token>\w+)/$",
            LenderBorrowerConsumer.as_asgi()),


]
