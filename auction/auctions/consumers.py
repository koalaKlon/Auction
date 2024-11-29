from channels.generic.websocket import AsyncWebsocketConsumer
import json


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'

        # Подключение к группе
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Перенаправление данных другим клиентам
        await self.channel_layer.group_send(
            self.auction_group_name,
            {
                'type': 'auction_update',
                'message': data['message']
            }
        )

    async def auction_update(self, event):
        message = event['message']

        # Отправка данных клиенту
        await self.send(text_data=json.dumps({
            'message': message
        }))
