import asyncio
import json
import os
from typing import Dict, Any, Callable
import aio_pika
from aio_pika import Message, DeliveryMode
import logging

logger = logging.getLogger(__name__)

class MessageBroker:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            logger.warning("Continuing without RabbitMQ - some features may not work")
            # Don't raise exception, just log warning
            self.connection = None
            self.channel = None

    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()

    async def publish_event(self, event_type: str, data: Dict[Any, Any], routing_key: str = None):
        """Publish an event to the message broker"""
        if not self.channel:
            await self.connect()
        
        if not self.channel:
            logger.warning(f"Cannot publish event {event_type} - RabbitMQ not available")
            return
        
        if routing_key is None:
            routing_key = event_type
        
        message_body = json.dumps({
            "event_type": event_type,
            "data": data,
            "timestamp": str(asyncio.get_event_loop().time())
        })
        
        message = Message(
            message_body.encode(),
            delivery_mode=DeliveryMode.PERSISTENT
        )
        
        await self.channel.default_exchange.publish(
            message,
            routing_key=routing_key
        )
        logger.info(f"Published event: {event_type}")

    async def subscribe_to_events(self, event_types: list, callback: Callable):
        """Subscribe to specific event types"""
        if not self.channel:
            await self.connect()
        
        if not self.channel:
            logger.warning(f"Cannot subscribe to events {event_types} - RabbitMQ not available")
            return
        
        # Declare a queue for this service
        queue_name = f"service_queue_{id(self)}"
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        # Bind to each event type
        for event_type in event_types:
            await queue.bind(exchange="", routing_key=event_type)
        
        # Start consuming
        async def process_message(message):
            async with message.process():
                try:
                    event_data = json.loads(message.body.decode())
                    await callback(event_data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        await queue.consume(process_message)
        logger.info(f"Subscribed to events: {event_types}")

# Global message broker instance
message_broker = None

async def get_message_broker():
    global message_broker
    if message_broker is None:
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
        message_broker = MessageBroker(rabbitmq_url)
        try:
            await message_broker.connect()
        except Exception as e:
            logger.warning(f"Failed to initialize message broker: {e}")
            # Return the broker instance anyway, it will handle failures gracefully
    return message_broker
