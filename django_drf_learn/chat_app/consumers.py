import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Fully asynchronous WebSocket consumer for real-time chat.
    Handles connect, disconnect, and message events.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is initiated.
        Joins the room group and accepts the connection.
        """
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        self.user = self.scope['user']

        # Reject unauthenticated connections
        if not self.user.is_authenticated:
            await self.close()
            return

        # Join room group via channel layer (Redis)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send last 20 messages from DB to the newly connected client
        messages = await self.get_last_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': msg['content'],
                'username': msg['username'],
                'timestamp': msg['timestamp'],
            }))

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection closes.
        Leaves the room group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket client.
        Saves the message to DB and broadcasts it to the group.
        """
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()

        if not message_content:
            return

        # Save message to database asynchronously
        await self.save_message(message_content)

        # Broadcast message to all clients in the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'username': self.user.username,
            }
        )

    async def chat_message(self, event):
        """
        Handler for 'chat_message' events from the channel layer.
        Sends the message to the WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': None,  # Real-time messages don't need a timestamp from DB
        }))

    # ------------------------------------------------------------------ #
    # Database helpers (sync → async via database_sync_to_async)          #
    # ------------------------------------------------------------------ #

    @database_sync_to_async
    def save_message(self, content):
        """Persist a chat message to the database."""
        room = Room.objects.get(slug=self.room_slug)
        Message.objects.create(
            room=room,
            user=self.user,
            content=content
        )

    @database_sync_to_async
    def get_last_messages(self):
        """Retrieve the last 20 messages for the current room."""
        try:
            room = Room.objects.get(slug=self.room_slug)
            messages = (
                Message.objects
                .filter(room=room)
                .select_related('user')
                .order_by('-timestamp')[:20]
            )
            return [
                {
                    'content': msg.content,
                    'username': msg.user.username,
                    'timestamp': msg.timestamp.strftime('%H:%M'),
                }
                for msg in reversed(list(messages))
            ]
        except Room.DoesNotExist:
            return []