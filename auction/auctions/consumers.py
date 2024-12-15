from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Auction, Bid, Chat
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

        # Send the message to WebSocket clients
        await self.send(text_data=json.dumps({
            'message': message
        }))

        # If the auction is finished, send a specific notification
        if message.get('status') == 'finished':
            await self.channel_layer.group_send(
                self.auction_group_name,
                {
                    'type': 'notify_auction_end',
                    'winner': message.get('winner'),
                }
            )

    async def notify_auction_end(self, event):
        # Notify all connected clients
        await self.send(text_data=json.dumps({
            'status': 'finished',
            'winner': event['winner']
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f"auction_{self.auction_id}_chat"

        # Add to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Discard from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender_name = text_data_json.get('sender')  # Название ключа должно совпадать с отправляемым из WebSocket

        if not message or not sender_name:
            return  # Игнорируем некорректные сообщения

        # Fetch auction and related objects asynchronously
        auction = await database_sync_to_async(Auction.objects.get)(id=self.auction_id)
        buyer = await database_sync_to_async(lambda: auction.buyer)()
        seller = await database_sync_to_async(lambda: auction.seller)()

        # Save the message to the database
        await database_sync_to_async(Chat.objects.create)(
            auction=auction,
            buyer=buyer,
            seller=seller,
            message=message,
            sender_name=sender_name
        )

        # Send the message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_name': sender_name
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_name = event['sender_name']
        print(f"New WebSocket message received: {message} from {sender_name}")
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_name': sender_name
        }))




