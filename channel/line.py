import asyncio
import base64
import hashlib
import hmac
import inspect
import json
import logging
from asyncio import CancelledError, Queue

import rasa
from rasa.core.channels import CollectingOutputChannel
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, List, Dict, Any, Callable, Awaitable, Iterable, Optional

from rasa.core.channels.channel import UserMessage, OutputChannel, InputChannel, QueueOutputChannel, logger
from linebot import (
    LineBotApi, WebhookHandler, utils as line_utils
)
from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton, MessageAction, ImageSendMessage, TemplateSendMessage,
    ButtonsTemplate, CarouselTemplate, CarouselColumn
)
from linebot.exceptions import (
    InvalidSignatureError
)

_image_url = "https://i.ibb.co/5G023yb/eunha.jpg"

class TheMessage:

    @classmethod
    def name(cls):
        return 'line'

    def __init__(
        self,
        page_access_token: Text,
        on_new_message: Callable[[UserMessage], Awaitable[None]],
    ) -> None:
        self.on_new_message = on_new_message
        self.client = LineBotApi(channel_access_token=page_access_token)
        self.event = {}  # type: Dict[Text, Any]

    def _get_user_id(self) -> Text:
        # ["source"]["userId"]
        return self.event.get("source", {}).get("userId", "")

    def _get_reply_token(self) -> Text:
        print(f"TOKEN: {self.event}")
        return self.event.get("replyToken")

    @staticmethod
    def _is_audio_message(message: Dict[Text, Any]) -> bool:
        return message["type"] == "audio"

    @staticmethod
    def _is_text_message(message: Dict[Text, Any]) -> bool:
        return message["type"] == "text"

    @staticmethod
    def _is_image_message(message: Dict[Text, Any]) -> bool:
        return message["type"] == "image"

    @staticmethod
    def _is_sticker_message(message: Dict[Text, Any]) -> bool:
        return message["type"] == "sticker"

    async def handle(self, event_payload: Dict[Text, Any]):
        logger.debug(f'EVENT PAYLOAD: {event_payload}')
        if not self.is_test_verify_webhook(event_payload):
            for evt in event_payload.get('events'):
                self.event = evt
                if evt.get('type') == 'message':
                    return await self.message(evt)
                else:
                    logger.warning(
                        "Received event type from Line that can not "
                        "handle: {}".format(evt["type"])
                    )
        return

    @staticmethod
    def is_test_verify_webhook(event: Dict[Text, Any]):
        if "destination" not in event:
            logger.debug(
                "Line webhook has been verified"
            )
            return True
        return False

    async def message(self, event: Dict[Text, Any]) -> None:
        message = event.get("message")
        if self._is_text_message(message):
            text = message.get("text")
        else:
            logger.warning(
                "Received message type from Line that can not "
                "handle: {}".format(message.get("type"))
            )
            return

        await self._handle_user_message(
            user_text=text,
            sender_id=self._get_user_id(),
            reply_token=self._get_reply_token()
        )

    async def _handle_user_message(
            self,
            user_text: Text,
            sender_id: Text,
            reply_token: Text,
    ) -> None:
        output_channel = LineBot(self.client, reply_token)
        # print(f"OUTPUT: {output_channel}")
        user_msg = UserMessage(
            text=user_text,
            output_channel=output_channel,
            sender_id=sender_id,
            input_channel=self.name())

        # noinspection PyBroadException
        try:
            await self.on_new_message(user_msg)
        except Exception:
            logger.exception(
                "Exception when trying to handle webhook for Line"
            )
            pass


class LineBot(OutputChannel):
    @classmethod
    def name(cls):
        return "line"

    def __init__(self, line_bot_api: LineBotApi, reply_token: Text):
        self.reply_token = reply_token
        self.line_bot_api = line_bot_api
        super(LineBot, self).__init__()
        self.messages = []
        self.test = 0

    async def send_response(self, recipient_id: Text, message: Dict[Text, Any]) -> None:
        self.test += 1
        print(f'TEST: {self.test}')
        print("MESSAGE IS {}".format(message))

        if message.get("quick_replies"):
            await self.send_quick_replies(
                recipient_id,
                message.pop("text"),
                message.pop("quick_replies"),
                **message
            )
        elif message.get("buttons"):
            await self.send_text_with_buttons(
                recipient_id, message.pop("text"), message.pop("buttons"), **message
            )
        if message.get("text"):
            await self.send_text_message(recipient_id, message.pop("text"), **message)
        if message.get("image"):
            await self.send_image_url(recipient_id, message.pop("image"), **message)
        self.send()

    def send(self):
        print(f'MESSAGE TO SEND: {self.messages}')
        self.line_bot_api.reply_message(self.reply_token, self.messages)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any
    ) -> None:
        quick_reply_buttons = []
        for button in buttons:
            quick_reply_buttons.append(
                QuickReplyButton(
                    action=MessageAction(
                        label=button.get("payload"),
                        text=button.get("title")
                    ),
                    image_url=button.get('image')
                )
            )

        self.messages.append(
            TextSendMessage(
                text=text,
                quick_reply=QuickReply(
                    items=quick_reply_buttons
                )
            )
        )

    async def send_image_url(
            self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        print(f"IMAGE: {image}")
        self.messages.append(
            ImageSendMessage(
                original_content_url=image,
                preview_image_url=image
            )
        )
        print(f'MESSAGE TO SEND: {self.messages}')

    async def send_text_message(self, recipient_id: Text, text: Text, **kwargs: Any) -> None:
        # self.line_bot_api.reply_message(self.reply_token, TextSendMessage(text))
        print(f"RECIPIENT ID: {recipient_id}")
        print(f"TEXT TO USER: {text}")
        self.messages.append(
            TextSendMessage(text)
        )
        print(f'MESSAGE TO SEND: {self.messages}')

        # button_template_message = TemplateSendMessage(
        #     alt_text="template message",
        #     template=ButtonsTemplate(
        #         thumbnail_image_url="https://i.ibb.co/5G023yb/eunha.jpg",
        #         title="First Menu",
        #         text="Subtitle",
        #         actions=[
        #             MessageAction(
        #                 label="label 1",
        #                 text="label 1"
        #             ),
        #             MessageAction(
        #                 label="label 2",
        #                 text="label 2"
        #             ),
        #             MessageAction(
        #                 label="label 3",
        #                 text="label 3"
        #             )
        #         ]
        #     )
        # )

        # carousel_template_message = TemplateSendMessage(
        #     alt_text="Carousel Template",
        #     template=CarouselTemplate(
        #         columns=[
        #             CarouselColumn(
        #                 thumbnail_image_url="https://i.ibb.co/5G023yb/eunha.jpg",
        #                 title="First Menu",
        #                 text="Subtitle 1",
        #                 actions=[
        #                     MessageAction(
        #                         label="label 1",
        #                         text="label 1"
        #                     ),
        #                     MessageAction(
        #                         label="label 2",
        #                         text="label 2"
        #                     ),
        #                     MessageAction(
        #                         label="label 3",
        #                         text="label 3"
        #                     )
        #                 ]
        #             ),
        #             CarouselColumn(
        #                 thumbnail_image_url="https://i.ibb.co/5G023yb/eunha.jpg",
        #                 title="Second Menu",
        #                 text="Subtitle 2",
        #                 actions=[
        #                     MessageAction(
        #                         label="label 1",
        #                         text="label 1"
        #                     ),
        #                     MessageAction(
        #                         label="label 2",
        #                         text="label 2"
        #                     ),
        #                     MessageAction(
        #                         label="label 3",
        #                         text="label 3"
        #                     )
        #                 ]
        #             )
        #         ]
        #     )
        # )


class LineChannel(InputChannel):
    """A custom http input channel.

    This implementation is the basis for a custom implementation of a chat
    frontend. You can customize this to send messages to Rasa Core and
    retrieve responses from the agent."""

    @classmethod
    def name(cls):
        return "line"

    @classmethod
    def from_credentials(cls, credentials):
        if not credentials:
            cls.raise_missing_credentials_exception()
        return cls(
            credentials.get('line_user_id'),
            credentials.get('line_secret'),
            credentials.get('line_token')
        )

    def __init__(
            self,
            line_user_id: Text,
            line_secret: Text,
            line_token: Text,
    ) -> None:
        self.line_token = line_token
        self.line_secret = line_secret
        self.line_user_id = line_user_id

    @staticmethod
    def validate_line_signatures(line_secret, body, signature) -> bool:
        key = bytearray(line_secret, 'utf-8')
        gen_signature = hmac.new(key, body, hashlib.sha256).digest()
        signature = signature.encode("UTF-8")
        logger.debug(f'SIGNATURE: {signature}')
        logger.debug(f'SIGNATURE: {type(signature)}')
        if hasattr(hmac, "compare_digest"):
            valid = hmac.compare_digest(signature, base64.b64encode(gen_signature))
            logger.debug(f"valid is {valid}")
        else:
            valid = line_utils.safe_compare_digest(signature, base64.b64encode(gen_signature))
            logger.debug(f"valid is {valid}")
        return valid

    def blueprint(
            self,
            # on_new_message,
            on_new_message: Callable[[UserMessage], Awaitable[None]]
    ):
        line_webhook = Blueprint("line_webhook", __name__)

        # noinspection PyUnusedLocal
        @line_webhook.route("/", methods=["GET"])
        async def health(request: Request):
            print("THIS IS HEALTH")
            return response.json({"status": "ok"})

        @line_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request):
            body = request.body
            body_json = request.json
            body_header = request.headers

            print(f"REQUEST BODY: {body}")
            print(f"REQUEST JSON: {body_json}")
            print(f"REQUEST HEADER: {body_header}")
            print(f"TYPE: {type(body)}")
            print(f"TYPE: {type(body_json)}")

            # check signature
            signature = request.headers['X-Line-Signature']
            if not self.validate_line_signatures(self.line_secret, body, signature):
                logger.warning(
                    "Wrong Line secret! Make sure this matches "
                    "the secret from your Line console"
                )
                return response.text("not validated")

            the_message = TheMessage(page_access_token=self.line_token, on_new_message=on_new_message)
            await the_message.handle(body_json)

            return response.text("success")

        return line_webhook
