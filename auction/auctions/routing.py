from django.urls import path
from .consumers import AuctionConsumer, ChatConsumer

websocket_urlpatterns = [
    path('ws/auction/<int:auction_id>/', AuctionConsumer.as_asgi()),
    path('ws/auction/<int:auction_id>/chat/', ChatConsumer.as_asgi())
]
