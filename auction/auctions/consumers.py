from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Auction, Bid
import json


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'

        # Принятие соединения (только один раз)
        await self.accept()

        # Подключение к группе WebSocket
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )

        # Получаем аукцион и определяем текущего лидера через ставки
        auction = await database_sync_to_async(Auction.objects.get)(id=self.auction_id)

        # Находим пользователя, сделавшего наибольшую ставку
        current_bid = str(auction.current_bid)
        current_leader = await self.get_current_leader(auction)

        await self.send(text_data=json.dumps({
            'message': {
                'current_bid': current_bid,
                'current_leader': current_leader
            }
        }))

    async def get_current_leader(self, auction):
        # Находим ставку с максимальной суммой для данного аукциона
        highest_bid = await self.get_highest_bid(auction)
        if highest_bid:
            return highest_bid.buyer.username
        return None

    @database_sync_to_async
    def get_highest_bid(self, auction):
        # This is a synchronous function to get the highest bid
        return Bid.objects.filter(auction=auction).order_by('-amount').first()

    async def disconnect(self, close_code):
        # Отключение от группы WebSocket
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Перенаправляем полученные данные другим клиентам
        await self.channel_layer.group_send(
            self.auction_group_name,
            {
                'type': 'auction_update',
                'message': data['message']
            }
        )

    async def auction_update(self, event):
        message = event['message']

        # Отправляем данные клиенту
        await self.send(text_data=json.dumps({
            'message': message
        }))
